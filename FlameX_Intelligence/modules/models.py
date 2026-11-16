"""Auditable grouped cross-validation and cautious scenario interpolation."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.metrics import (mean_absolute_error,mean_squared_error,r2_score,
    f1_score,precision_recall_fscore_support,confusion_matrix,log_loss)
from sklearn.neighbors import NearestNeighbors

REG_FIELDS=['fuel','oxygen','pressure','diameter']
CLASS_FIELDS=['fuel','oxygen','pressure','diameter','co','helium']

def feature_pipeline(fields):
    num=[f for f in fields if f!='fuel']
    return ColumnTransformer([
        ('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num),
        ('fuel',OneHotEncoder(handle_unknown='ignore'),['fuel'])
    ])

def regression_analysis(df,trees=130):
    available=[f for f in REG_FIELDS if f in df]
    needed=[f for f in available if f!='diameter']+['burn']
    q=df.dropna(subset=needed).copy()
    if len(q)<45 or q['pressure'].nunique()<6 or 'fuel' not in available:
        return {'error':'Not enough complete records and pressure diversity for grouped cross-validation.'}
    # Explicit complete-case model cohort: only used for modeling, not deleted from source
    q=q.dropna(subset=available)
    if len(q)<45:return {'error':'Too few rows with complete model inputs.'}
    unique_pressure = pd.Series(sorted(q['pressure'].unique()))
    pressure_groups = pd.qcut(unique_pressure.rank(method='first'),q=4,labels=False,duplicates='drop')
    group_map = dict(zip(unique_pressure.tolist(),pressure_groups.tolist()))
    group = q['pressure'].map(group_map).astype(int)
    group_n=group.nunique()
    if group_n<3:return {'error':'Grouped CV requires at least three pressure regimes.'}
    splitter=GroupKFold(n_splits=int(group_n))
    X=q[available]; y=q['burn'].to_numpy(float)
    builds={
        'Mean baseline':DummyRegressor(strategy='mean'),
        'Linear (ridge)':Pipeline([('pre',feature_pipeline(available)),('est',Ridge(alpha=1.0))]),
        'Random Forest':Pipeline([('pre',feature_pipeline(available)),('est',RandomForestRegressor(n_estimators=trees,min_samples_leaf=3,random_state=32,n_jobs=-1))])
    }
    rows=[]; oof={}; folds=[]
    for name,model in builds.items():
        preds=np.full(len(q),np.nan)
        for k,(itr,ite) in enumerate(splitter.split(X,y,groups=group)):
            model.fit(X.iloc[itr],y[itr]); yp=model.predict(X.iloc[ite])
            preds[ite]=yp
            folds.append({'Model':name,'Fold':k+1,'N':len(ite),'MAE':mean_absolute_error(y[ite],yp),'Pressure group':int(group.iloc[ite].iloc[0])})
        oof[name]=preds
        rows.append({'Model':name,'Grouped CV MAE':mean_absolute_error(y,preds),
                     'Grouped CV RMSE':np.sqrt(mean_squared_error(y,preds)),'Grouped CV R²':r2_score(y,preds),'Rows':len(q)})
    final=Pipeline([('pre',feature_pipeline(available)),('est',RandomForestRegressor(n_estimators=trees,min_samples_leaf=3,random_state=32,n_jobs=-1))])
    final.fit(X,y)
    residuals=np.abs(y-oof['Random Forest'])
    radius=float(np.quantile(residuals,.90))
    # An exploratory residual band, NOT conditional coverage guarantee
    importances=final.named_steps['est'].feature_importances_
    names=final.named_steps['pre'].get_feature_names_out()
    importance=pd.DataFrame({'Feature':names,'Importance':importances}).sort_values('Importance',ascending=False)
    return {'summary':pd.DataFrame(rows),'folds':pd.DataFrame(folds),'frame':q,
        'oof':pd.DataFrame({'Measured':y,'Baseline':oof['Mean baseline'],'Linear':oof['Linear (ridge)'],'Random Forest':oof['Random Forest'],'Record':q['record_id'].to_numpy()}),
        'model':final,'features':available,'interval_halfwidth':radius,
        'importance':importance,'pressure_bins':int(group_n),'method':'Four pressure-rank quartile groups; GroupKFold; pooled out-of-fold scores'}

def classification_analysis(df,trees=140):
    if not set(CLASS_FIELDS+['outcome']).issubset(df):return {'error':'Required outcome features unavailable'}
    q=df.dropna(subset=CLASS_FIELDS+['outcome']).copy()
    labels=sorted(q['outcome'].unique().tolist())
    if len(q)<60 or len(labels)<3 or q['outcome'].value_counts().min()<10:
        return {'error':'Insufficient class counts for stratified 5-fold validation'}
    X=q[CLASS_FIELDS]; y=q['outcome'].to_numpy(str)
    k=min(5,int(q['outcome'].value_counts().min()))
    cv=StratifiedKFold(n_splits=k,shuffle=True,random_state=42)
    preds=np.empty(len(q),dtype=object); prob=np.full((len(q),len(labels)),np.nan)
    for train,test in cv.split(X,y):
        pipe=Pipeline([('pre',feature_pipeline(CLASS_FIELDS)),('clf',RandomForestClassifier(n_estimators=trees,class_weight='balanced',min_samples_leaf=2,random_state=42,n_jobs=-1))])
        pipe.fit(X.iloc[train],y[train]);preds[test]=pipe.predict(X.iloc[test]);proba=pipe.predict_proba(X.iloc[test])
        for j,lab in enumerate(pipe.named_steps['clf'].classes_):prob[test,labels.index(lab)]=proba[:,j]
    pr,rc,f1,support=precision_recall_fscore_support(y,preds,labels=labels,zero_division=0)
    macro=float(f1_score(y,preds,average='macro'))
    eye=np.eye(len(labels))[pd.Categorical(y,categories=labels).codes]
    brier=float(np.mean(np.sum((prob-eye)**2,axis=1)))
    ll=float(log_loss(y,prob,labels=labels))
    reliable=bool(macro>=.55 and np.min(rc)>=.4)
    conf=pd.DataFrame(confusion_matrix(y,preds,labels=labels),index=labels,columns=labels)
    metrics=pd.DataFrame({'Class':labels,'Precision':pr,'Recall':rc,'F1':f1,'Support':support})
    confidence=np.max(prob,axis=1);correct=(preds==y).astype(int)
    calibration=pd.DataFrame({'Confidence':confidence,'Correct':correct,'bin':pd.cut(confidence,bins=[0,.2,.4,.6,.8,1.00001],include_lowest=True)}).groupby('bin',observed=True).agg({'Confidence':'mean','Correct':['mean','count']})
    calibration.columns=['Mean confidence','Observed accuracy','N']
    return {'rows':len(q),'labels':labels,'macro_f1':macro,'brier':brier,'logloss':ll,'metrics':metrics,
            'confusion':conf,'reliable':reliable,'calibration':calibration.reset_index(),'folds':k,
            'note':'Stratified cross-validation is not grouped by pressure; probabilities require external validation and calibration before safety use.'}


def scenario_neighbors(df,scenario,k=6):
    q=df.dropna(subset=['fuel','oxygen','pressure','diameter']).copy()
    q=q[q['fuel']==scenario['fuel']]
    if q.empty:return {'domain':'OUTSIDE','neighbors':q,'distance':np.inf,'reason':'No historical observations for this fuel.'}
    fields=['oxygen','pressure','diameter']
    vals=q[fields].to_numpy(float); target=np.array([scenario[f] for f in fields],dtype=float)
    scale=np.maximum(vals.max(axis=0)-vals.min(axis=0),1e-9)
    d=np.linalg.norm((vals-target)/scale,axis=1)
    idx=np.argsort(d)[:k];n=q.iloc[idx].copy();n['normalized_distance']=d[idx]
    outside=[f for f,x in zip(fields,target) if x<q[f].min() or x>q[f].max()]
    # Joint-support threshold based on leave-one-out nearest-neighbor distances
    nnd=NearestNeighbors(n_neighbors=min(2,len(q))).fit(vals/scale)
    selfdist=nnd.kneighbors(vals/scale)[0]
    reference=np.quantile(selfdist[:,1],.95) if len(q)>1 else 0
    nearest=float(np.min(d))
    if outside: status='OUTSIDE'; reason='Outside observed '+', '.join(outside)+' range(s).'
    elif nearest>max(float(reference)*2,.075):status='OUTSIDE'; reason='No nearby observations under jointly similar conditions.'
    elif nearest>max(float(reference),.04):status='NEAR EDGE';reason='Sparse joint coverage relative to historical neighboring records.'
    else:status='INSIDE';reason='Comparable historical conditions are represented nearby.'
    return {'domain':status,'neighbors':n,'distance':nearest,'reason':reason,'reference_distance':float(reference)}


def scenario_prediction(regression,scenario,neighbors,moon_band=False):
    if 'error' in regression:return {'prediction':None,'reason':regression['error']}
    if neighbors['domain']=='OUTSIDE':return {'prediction':None,'reason':neighbors['reason']}
    if moon_band:
        return {'prediction':None,'reason':'The specified atmosphere lies in an unsupported joint experimental region; withholding an extrapolated prediction. NASA reference points are not safety thresholds.'}
    x=pd.DataFrame([{f:scenario[f] for f in regression['features']}])
    p=float(regression['model'].predict(x)[0]);hw=regression['interval_halfwidth']
    return {'prediction':p,'lower':p-hw,'upper':p+hw,'radius':hw,
            'method':'Random Forest full-data fit; ±90th percentile absolute grouped-CV error. Exploratory empirical band, not a guaranteed 90% prediction interval.'}
