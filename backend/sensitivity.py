"""Deterministic, same-price-year financial sensitivities; no invented price."""
import math
from .work_packages import package,regional_model,settings_for

def cash_case(capex,fixed,variable,decommission,rate,life,net,price=None,delay=0):
    years=range(delay+1,delay+life+1);annuity=sum((1+rate)**-t for t in years);energy_pv=net*annuity
    if energy_pv<=0:raise ValueError('Positive discounted delivered energy is required')
    cost=capex+(fixed+variable*net)*annuity+decommission/(1+rate)**(delay+life)
    npv=None if price is None else net*price*annuity-cost
    return {'lcoe_gbp_mwh':cost/energy_pv,'npv_gbp':npv,'pv_cost_gbp':cost,'pv_energy_mwh':energy_pv,'delay_years':delay}

def analyze_sensitivity(s,ctx):
    from .engineering import energy,layout
    result=package('C61',s,ctx);data,provenance,gaps=result;wp=data['work_package'];i=s['inputs'];cfg=settings_for(s,'C61')
    try:regional=regional_model(s,ctx)
    except ValueError as error:gaps.append(str(error));return data,provenance,gaps
    if regional:
        b,provenance,base_gaps=regional;gaps+=base_gaps;variable=b['benchmark']['variable_om_gbp_mwh'];wake=next(r['fraction'] for r in b['losses'] if r['name']=='wake_loss');net=b['net_aep_mwh'];capex=b['capex_gbp'];fixed=b['annual_opex_gbp'];decomm=b['decommission_gbp'];rate=b['discount_rate'];year=b['price_year'];life=b['lifetime_years']
    else:
        fields=['wake_loss','electrical_loss','availability_loss','curtailment_loss','uncertainty_fraction','capex_gbp_per_kw','opex_gbp_per_kw_year','decommission_gbp','discount_rate']
        if not ctx.get('wind') or not i.get('aoi') or any(i.get(k) is None for k in fields):
            gaps.append('Connect the regional energy/cost case, or supply a valid AOI, site wind and complete same-price-year cost assumptions.');return data,provenance,gaps
        try:layout(i,s['layout_id'],ctx['wind']);en=energy(i,ctx['wind'])
        except ValueError as error:gaps.append(str(error));return data,provenance,gaps
        net=en['net_aep_mwh'];capex=i['capacity_mw']*1000*i['capex_gbp_per_kw'];fixed=i['capacity_mw']*1000*i['opex_gbp_per_kw_year'];decomm=i['decommission_gbp'];rate=i['discount_rate'];year=i['price_year'];life=i['lifetime_years'];variable=0;wake=i['wake_loss'];provenance=[ctx['wind_meta']]
    price=cfg['price'] if cfg['price'] is not None else i.get('power_price_gbp_mwh') if i['price_year']==year else None
    base={'capex':capex,'fixed':fixed,'variable':variable,'decommission':decomm,'rate':rate,'life':life,'net':net,'price':price,'delay':0};central=cash_case(**base);v=cfg['variation_pct']/100;rate_d=cfg['rate_delta_pct']/100;wake_d=cfg['wake_delta_pct']/100
    variants=[('CAPEX','capex',capex*(1-v),capex*(1+v),'real GBP'),('Fixed OPEX','fixed',fixed*(1-v),fixed*(1+v),'real GBP/year'),('Real discount rate','rate',max(0,rate-rate_d),min(.5,rate+rate_d),'fraction'),('Wake loss','net',net*(1-max(0,wake-wake_d))/(1-wake),net*(1-min(.9,wake+wake_d))/(1-wake),'net MWh/year'),('Commissioning delay','delay',0,int(cfg['delay_years']),'years')]
    if price is not None:variants.append(('Captured electricity price','price',min(price*(1-v),price*(1+v)),max(price*(1-v),price*(1+v)),'real GBP/MWh'))
    sensitivities=[]
    for name,key,low,high,unit in variants:
        a=cash_case(**{**base,key:low});b=cash_case(**{**base,key:high});sensitivities.append({'name':name,'parameter':key,'low_input':low,'high_input':high,'unit':unit,'low':a,'high':b})
    for item in sensitivities:
        if item['name']=='Wake loss':item.update(parameter='wake_loss',low_input=max(0,wake-wake_d),high_input=min(.9,wake+wake_d),unit='fraction')
    price_axis=sorted({price*f for f in [.6,.8,1,1.2,1.4]}) if price is not None else []
    rates=sorted(set([max(0,rate-2*rate_d),max(0,rate-rate_d),rate,min(.5,rate+rate_d),min(.5,rate+2*rate_d)]));heatmap=[{'price':p,'rate':r,**cash_case(**{**base,'price':p,'rate':r})} for r in rates for p in price_axis]
    wp['financial']={'base':central,'sensitivity':sensitivities,'heatmap':heatmap,'price_year':year,'captured_price':price,'base_rate':rate,'base_net_mwh':net,'base_wake_loss':wake,'variation_pct':cfg['variation_pct']}
    wp['metrics']=[{'name':'Central LCOE','value':central['lcoe_gbp_mwh'],'unit':f'real {year} GBP/MWh'},{'name':'Central unlevered NPV','value':central['npv_gbp']/1e6 if central['npv_gbp'] is not None else None,'unit':f'million real {year} GBP'}];wp['quantitative_ready']=True
    wp['method']='Deterministic one-at-a-time cost, real discount-rate, wake-loss and commissioning-delay sensitivities. CAPEX stays at year 0; operating energy/revenue/OPEX and terminal removal shift with delay. No holding costs or construction phasing are invented. Price changes NPV, not cost-based LCOE. No probability distributions or Monte Carlo confidence claims.'
    wp['assumptions'] += [{'name':'Captured price','value':price,'unit':f'real {year} GBP/MWh','basis':'User assumption; absent means NPV unavailable'},{'name':'Price and cost basis','value':year,'unit':'real GBP price year','basis':'All financial amounts use this same price year'}]
    if price is None:gaps.append(f'Enter an assumed captured price in real {year} GBP/MWh to enable NPV, price sensitivity and the price/discount heatmap. No electricity price is silently assumed.')
    return data,provenance,gaps
