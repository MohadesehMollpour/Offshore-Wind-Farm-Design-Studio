"""Extract JSON from the attached page without running its scripts."""
import argparse,hashlib,json,re
from pathlib import Path
from backend.engine import digest,now
from backend.references import REFERENCE_DIR,validate_farms

def main():
    parser=argparse.ArgumentParser();parser.add_argument('html');args=parser.parse_args()
    path=Path(args.html);raw=path.read_bytes();text=raw.decode('utf-8-sig')
    match=re.search(r'\bconst\s+D\s*=\s*',text)
    if not match:raise ValueError('The attachment does not contain the expected JSON data block')
    data,_=json.JSONDecoder().raw_decode(text,match.end());validate_farms(data)
    sha=hashlib.sha256(raw).hexdigest();REFERENCE_DIR.mkdir(parents=True,exist_ok=True)
    original=sha+'.html';(REFERENCE_DIR/original).write_bytes(raw)
    record={'metadata':{'title':'Wind farms around Hornsea','source_filename':path.name,'original_filename':original,'original_sha256':sha,'data_sha256':digest(data),'imported_at':now(),'classification':'user_supplied_reference_snapshot','verification':'Not independently verified; claims and dates retained from the attachment.','claimed_as_of':data.get('energyNumbersAsOf'),'placement':'C37 nearby wind-farm comparison; context for C38 cumulative effects.','original_download_url':'/api/references/hornsea-farms/original','claimed_sources':[{'name':'EnergyNumbers capacity factors','url':'https://energynumbers.info/uk-offshore-wind-capacity-factors'},{'name':'EMODnet Human Activities','url':'https://emodnet.ec.europa.eu/en/human-activities'},{'name':'Wikipedia UK offshore wind farms','url':'https://en.wikipedia.org/wiki/List_of_offshore_wind_farms_in_the_United_Kingdom'}],'limitations':['Embedded values are a static user-supplied snapshot, not a live API feed.','Capacity factors, capacities, owners, dates and status claims require independent verification before use in a design calculation.','The drawing uses the attachment reference point and schematic SVG boundaries, not the project AOI or authoritative lease geometries.','The listed inventory is not verified as exhaustive. Missing capacity factors are unavailable, not zero.','No attachment data feeds the project energy, suitability or finance calculation.']},'data':data}
    (REFERENCE_DIR/'reference.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'farms':len(data['farms']),'map_only':len(data['mapOnly']),'original_sha256':sha,'directory':str(REFERENCE_DIR)},indent=2))

if __name__=='__main__':main()
