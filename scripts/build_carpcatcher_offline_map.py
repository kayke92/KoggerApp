#!/usr/bin/env python3
"""Build the bundled Carpcatcher OSM SQLite cache without scraping tile servers.

Overview levels contain a lightweight Netherlands outline. Detailed levels are
rendered locally from Geofabrik's open Limburg shapefile extract.
"""
import io, math, os, sqlite3, tempfile, urllib.request, zipfile
from pathlib import Path
import shapefile
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "resources/offline/tiles_osm.db"
SOURCE = "https://download.geofabrik.de/europe/netherlands/limburg-latest-free.shp.zip"
DETAIL = (5.60, 50.78, 5.98, 51.08)  # includes Stein, Meers, Geulle and Maastricht
NL = [(3.35,51.35),(3.75,51.85),(4.05,52.35),(4.55,52.95),(5.25,53.50),
      (6.10,53.55),(7.20,53.25),(7.05,52.55),(6.75,51.85),(6.20,50.75),
      (5.55,50.75),(5.05,51.05),(4.45,51.35)]

def tile_xy(lon, lat, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n
    lat = max(-85.0511, min(85.0511, lat))
    y = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n
    return x, y

def pixel(lon, lat, z, tx, ty):
    x, y = tile_xy(lon, lat, z)
    return ((x - tx) * 256.0, (y - ty) * 256.0)

def ranges(bounds, z):
    west, south, east, north = bounds
    x0, y1 = tile_xy(west, south, z); x1, y0 = tile_xy(east, north, z)
    return range(math.floor(x0), math.floor(x1) + 1), range(math.floor(y0), math.floor(y1) + 1)

def put(db, x, y, z, im):
    data = io.BytesIO(); im.convert("RGB").save(data, "JPEG", quality=86, optimize=True)
    db.execute("INSERT OR REPLACE INTO tiles(x,y,z,image) VALUES(?,?,?,?)", (x,y,z,data.getvalue()))

def draw_overview(db):
    bounds = (3.2, 50.65, 7.35, 53.65)
    for z in range(6, 11):
        xs, ys = ranges(bounds, z)
        for x in xs:
            for y in ys:
                im = Image.new("RGB", (256,256), "#b7d7ee"); d = ImageDraw.Draw(im)
                poly = [pixel(lon,lat,z,x,y) for lon,lat in NL]
                d.polygon(poly, fill="#e8e4d8", outline="#6c7b68", width=2)
                put(db,x,y,z,im)

def read_layers(folder):
    specs = [
      ("gis_osm_landuse_a_free_1.shp", "poly", "#d9e4ca", 1),
      ("gis_osm_water_a_free_1.shp", "poly", "#92c5e8", 2),
      ("gis_osm_waterways_free_1.shp", "line", "#6daed6", 2),
      ("gis_osm_roads_free_1.shp", "line", "#d9a86c", 2),
      ("gis_osm_buildings_a_free_1.shp", "poly", "#c9b6a4", 1),
    ]
    layers=[]
    for name, kind, color, width in specs:
        p=next(folder.rglob(name), None)
        if not p: continue
        r=shapefile.Reader(str(p)); shapes=[]
        for s in r.iterShapes():
            if s.bbox[2] < DETAIL[0] or s.bbox[0] > DETAIL[2] or s.bbox[3] < DETAIL[1] or s.bbox[1] > DETAIL[3]: continue
            shapes.append(s)
        layers.append((kind,color,width,shapes))
    return layers

def draw_detail(db, layers):
    for z in range(10, 17):
        xs, ys = ranges(DETAIL,z)
        buckets={(x,y):[] for x in xs for y in ys}
        for li,(_,_,_,shapes) in enumerate(layers):
            for s in shapes:
                sx,sy=ranges((s.bbox[0],s.bbox[1],s.bbox[2],s.bbox[3]),z)
                for x in sx:
                    for y in sy:
                        if (x,y) in buckets: buckets[(x,y)].append((li,s))
        for (x,y), items in buckets.items():
            im=Image.new("RGB",(256,256),"#eeeade"); d=ImageDraw.Draw(im)
            for li,s in items:
                kind,color,width,_=layers[li]
                cuts=list(s.parts)+[len(s.points)]
                for a,b in zip(cuts,cuts[1:]):
                    pts=[pixel(lon,lat,z,x,y) for lon,lat in s.points[a:b]]
                    if len(pts)<2: continue
                    if kind=="poly" and len(pts)>=3: d.polygon(pts,fill=color)
                    else: d.line(pts,fill=color,width=width,joint="curve")
            put(db,x,y,z,im)
        db.commit()

def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if OUT.exists(): OUT.unlink()
    req=urllib.request.Request(SOURCE,headers={"User-Agent":"Carpcatcher-Control offline map builder"})
    with urllib.request.urlopen(req,timeout=180) as response: raw=response.read()
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); zipfile.ZipFile(io.BytesIO(raw)).extractall(root)
        db=sqlite3.connect(OUT)
        db.execute("CREATE TABLE tiles(x INTEGER,y INTEGER,z INTEGER,image BLOB,PRIMARY KEY(x,y,z))")
        draw_overview(db); draw_detail(db,read_layers(root)); db.commit(); db.close()
    print(f"Created {OUT} ({OUT.stat().st_size/1024/1024:.1f} MiB)")

if __name__ == "__main__": main()
