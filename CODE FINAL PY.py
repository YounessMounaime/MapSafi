import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import folium
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from folium.plugins import FloatImage
from pyproj import Transformer
from folium.plugins import MeasureControl


# Variables globales
gdf = None
geojson_gdf = None
centre = None
titres_active = True
dossier_donnees = "data"
geojson_active = True
intersections_active = True
couche_travail_active = "titres"  # peut être : "titres", "geojson", "intersection"


def charger_villes():
    fichiers = os.listdir(dossier_donnees)
    return [f.replace(".xlsx", "").upper() for f in fichiers if f.endswith(".xlsx")]

def charger_donnees(ville):
    global gdf, centre
    fichier_path = os.path.join(dossier_donnees, f"{ville}.xlsx")
    try:
        df = pd.read_excel(fichier_path)
        df["geometry"] = df["wkt_geom"].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
        gdf_proj = gdf.to_crs(epsg=32629)
        centre_proj = gdf_proj.geometry.unary_union.centroid
        centre = gpd.GeoSeries([centre_proj], crs="EPSG:32629").to_crs(epsg=4326).iloc[0]
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du chargement de {ville} : {e}")
        gdf = None
        centre = None

def charger_geojson():
    global geojson_gdf
    chemins = filedialog.askopenfilenames(filetypes=[("Fichier GeoJSON", "*.geojson")])
    if chemins:
        try:
            geojsons = [gpd.read_file(chemin).to_crs(epsg=4326) for chemin in chemins]
            geojson_gdf = gpd.GeoDataFrame(pd.concat(geojsons, ignore_index=True)).set_crs(epsg=4326)
            messagebox.showinfo("Fichier chargé", f"{len(geojson_gdf)} entités GeoJSON chargées (multi-fichiers).")
        except Exception as e:
            messagebox.showerror("Erreur GeoJSON", f"Erreur de chargement : {e}")
            geojson_gdf = None
def analyser_intersection():
    if gdf is None or geojson_gdf is None:
        messagebox.showwarning("Données manquantes", "Veuillez charger une ville et un fichier GeoJSON.")
        return

    titres_proj = gdf.to_crs(epsg=32629)
    resultats = []

    for i, geojson_geom in enumerate(geojson_gdf.geometry):
        surface_geojson = geojson_geom.area
        for j, titre_row in titres_proj.iterrows():
            intersection = geojson_geom.intersection(titre_row.geometry)
            if not intersection.is_empty:
                surface_inter = intersection.area
                resultats.append({
                    "ID_GeoJSON": i + 1,
                    "Titre": titre_row["num"],
                    "Surface_GeoJSON (m²)": surface_geojson,
                    "Surface_Titre (m²)": titre_row.geometry.area,
                    "Intersection (m²)": surface_inter
                })

    if resultats:
        df_export = pd.DataFrame(resultats)
        nom_fichier = f"intersection_resultats_{int(time.time())}.xlsx"
        df_export.to_excel(nom_fichier, index=False)
        messagebox.showinfo("Export terminé", f"Résultats exportés vers {nom_fichier}")
        os.startfile(nom_fichier)
    else:
        messagebox.showinfo("Aucune intersection", "Aucune intersection trouvée.")
def analyser_intersection_geojson_geojson():
    if geojson_gdf is None or geojson_gdf.empty:
        messagebox.showwarning("Données manquantes", "Veuillez charger plusieurs fichiers GeoJSON.")
        return

    geojson_proj = geojson_gdf.to_crs(epsg=32629)
    intersections = []

    for i, geom1 in enumerate(geojson_proj.geometry):
        for j, geom2 in enumerate(geojson_proj.geometry):
            if i < j:
                inter = geom1.intersection(geom2)
                if not inter.is_empty:
                    intersections.append(inter)

    if not intersections:
        messagebox.showinfo("Aucune intersection", "Aucune intersection détectée entre les GeoJSON.")
        return

    gdf_inter = gpd.GeoDataFrame(geometry=intersections, crs="EPSG:32629").to_crs(epsg=4326)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    chemin = f"intersections_geojson_{timestamp}.geojson"
    gdf_inter.to_file(chemin, driver="GeoJSON")
    messagebox.showinfo("Export terminé", f"Intersections GeoJSON↔GeoJSON exportées vers {chemin}")
    os.startfile(chemin)
def ajouter_coordonnees_locales():
    points = []
    def ajouter_point():
        try:
            x = float(entry_x.get().strip())
            y = float(entry_y.get().strip().replace(",", "."))
            points.append((x, y))
            listbox_points.insert(tk.END, f"X: {x}, Y: {y}")
            entry_x.delete(0, tk.END)
            entry_y.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erreur", "Coordonnées invalides.")

import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import folium
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from folium.plugins import FloatImage
from pyproj import Transformer
from folium.plugins import MeasureControl


# Variables globales
gdf = None
geojson_gdf = None
centre = None
titres_active = True
dossier_donnees = "data"

def charger_villes():
    fichiers = os.listdir(dossier_donnees)
    return [f.replace(".xlsx", "").upper() for f in fichiers if f.endswith(".xlsx")]

def charger_donnees(ville):
    global gdf, centre
    fichier_path = os.path.join(dossier_donnees, f"{ville}.xlsx")
    try:
        df = pd.read_excel(fichier_path)
        df["geometry"] = df["wkt_geom"].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
        gdf_proj = gdf.to_crs(epsg=32629)
        centre_proj = gdf_proj.geometry.unary_union.centroid
        centre = gpd.GeoSeries([centre_proj], crs="EPSG:32629").to_crs(epsg=4326).iloc[0]
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du chargement de {ville} : {e}")
        gdf = None
        centre = None

def charger_geojson():
    global geojson_gdf
    chemins = filedialog.askopenfilenames(filetypes=[("Fichier GeoJSON", "*.geojson")])
    if chemins:
        try:
            geojsons = [gpd.read_file(chemin).to_crs(epsg=4326) for chemin in chemins]
            geojson_gdf = gpd.GeoDataFrame(pd.concat(geojsons, ignore_index=True)).set_crs(epsg=4326)
            messagebox.showinfo("Fichier chargé", f"{len(geojson_gdf)} entités GeoJSON chargées (multi-fichiers).")
        except Exception as e:
            messagebox.showerror("Erreur GeoJSON", f"Erreur de chargement : {e}")
            geojson_gdf = None

def analyser_intersection():
    if gdf is None or geojson_gdf is None:
        messagebox.showwarning("Données manquantes", "Veuillez charger une ville et un fichier GeoJSON.")
        return

    titres_proj = gdf.to_crs(epsg=32629)
    geojson_proj = geojson_gdf.to_crs(epsg=32629)
    resultats = []

    for i, geojson_geom in enumerate(geojson_proj.geometry):
        surface_geojson = geojson_geom.area
        for j, titre_row in titres_proj.iterrows():
            surface_titre = titre_row.geometry.area
            intersection = geojson_geom.intersection(titre_row.geometry)
            surface_inter = intersection.area if not intersection.is_empty else 0.0

            resultats.append({
                "ID_GeoJSON": i + 1,
                "Titre": titre_row["num"],
                "Surface_GeoJSON (m²)": round(surface_geojson, 2),
                "Surface_Titre (m²)": round(surface_titre, 2),
                "Intersection (m²)": round(surface_inter, 2)
            })

    # Export même si aucune intersection
    df_export = pd.DataFrame(resultats)
    nom_fichier = f"intersection_resultats_{int(time.time())}.xlsx"
    df_export.to_excel(nom_fichier, index=False)
    messagebox.showinfo("Export terminé", f"Résultats exportés vers {nom_fichier}")
    os.startfile(nom_fichier)
def analyser_intersection_geojson_geojson():
    if geojson_gdf is None or geojson_gdf.empty:
        messagebox.showwarning("Données manquantes", "Veuillez charger plusieurs fichiers GeoJSON.")
        return

    geojson_proj = geojson_gdf.to_crs(epsg=32629)
    intersections = []

    for i, geom1 in enumerate(geojson_proj.geometry):
        for j, geom2 in enumerate(geojson_proj.geometry):
            if i < j:
                inter = geom1.intersection(geom2)
                if not inter.is_empty:
                    intersections.append(inter)

    if not intersections:
        messagebox.showinfo("Aucune intersection", "Aucune intersection détectée entre les GeoJSON.")
        return

    gdf_inter = gpd.GeoDataFrame(geometry=intersections, crs="EPSG:32629").to_crs(epsg=4326)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    chemin = f"intersections_geojson_{timestamp}.geojson"
    gdf_inter.to_file(chemin, driver="GeoJSON")
    messagebox.showinfo("Export terminé", f"Intersections GeoJSON↔GeoJSON exportées vers {chemin}")
    os.startfile(chemin)


def ajouter_coordonnees_locales():
    points = []  # liste des tuples (nom, x, y)

    def ajouter_point():
        try:
            nom = entry_nom.get().strip()
            x = float(entry_x.get().strip())
            y = float(entry_y.get().strip().replace(",", "."))
            points.append((nom, x, y))
            listbox_points.insert(tk.END, f"{nom} - X: {x}, Y: {y}")
            entry_nom.delete(0, tk.END)
            entry_x.delete(0, tk.END)
            entry_y.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erreur", "Coordonnées invalides.")

    def remplir_champs(event):
        selection = listbox_points.curselection()
        if selection:
            nom, x, y = points[selection[0]]
            entry_nom.delete(0, tk.END)
            entry_nom.insert(0, nom)
            entry_x.delete(0, tk.END)
            entry_x.insert(0, str(x))
            entry_y.delete(0, tk.END)
            entry_y.insert(0, str(y))

    def modifier_point():
        index = listbox_points.curselection()
        if not index:
            messagebox.showwarning("Sélection manquante", "Sélectionnez un point à modifier.")
            return
        try:
            nom = entry_nom.get().strip()
            x_val = entry_x.get().strip()
            y_val = entry_y.get().strip().replace(",", ".")

            if not nom or not x_val or not y_val:
                raise ValueError("Champs vides ou incomplets.")

            x = float(x_val)
            y = float(y_val)
            points[index[0]] = (nom, x, y)
            listbox_points.delete(index[0])
            listbox_points.insert(index[0], f"{nom} - X: {x}, Y: {y}")
        except ValueError as e:
            messagebox.showerror("Erreur", f"Coordonnées invalides.\nDétails : {e}")

    def supprimer_point():
        index = listbox_points.curselection()
        if not index:
            messagebox.showwarning("Sélection manquante", "Sélectionnez un point à supprimer.")
            return
        listbox_points.delete(index[0])
        del points[index[0]]

    def afficher_points():
        nonlocal points
        epsg_selection = combo_epsg.get()
        code = 26191 if "26191" in epsg_selection else \
               26192 if "26192" in epsg_selection else \
               26194 if "26194" in epsg_selection else \
               26195 if "26195" in epsg_selection else 3857
        transformer = Transformer.from_crs(f"EPSG:{code}", "EPSG:4326", always_xy=True)
        transformed = [Point(*transformer.transform(x, y)) for _, x, y in points]
        global geojson_gdf
        if geojson_gdf is None:
            geojson_gdf = gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")
        if len(transformed) == 1:
            geojson_gdf = pd.concat([geojson_gdf, gpd.GeoDataFrame([{"geometry": transformed[0]}], geometry="geometry", crs="EPSG:4326")], ignore_index=True)
        else:
            polygon = Polygon([(pt.x, pt.y) for pt in transformed])
            geojson_gdf = pd.concat([geojson_gdf, gpd.GeoDataFrame([{"geometry": polygon}], geometry="geometry", crs="EPSG:4326")], ignore_index=True)
        fenetre_coords.destroy()

    # Interface
    fenetre_coords = tk.Toplevel(fenetre)
    fenetre_coords.title("Ajouter coordonnées locales")

    tk.Label(fenetre_coords, text="Nom du point :").grid(row=0, column=0)
    entry_nom = tk.Entry(fenetre_coords)
    entry_nom.grid(row=0, column=1)

    tk.Label(fenetre_coords, text="X :").grid(row=1, column=0)
    entry_x = tk.Entry(fenetre_coords)
    entry_x.grid(row=1, column=1)

    tk.Label(fenetre_coords, text="Y :").grid(row=2, column=0)
    entry_y = tk.Entry(fenetre_coords)
    entry_y.grid(row=2, column=1)

    tk.Label(fenetre_coords, text="Projection EPSG :").grid(row=3, column=0)
    combo_epsg = ttk.Combobox(fenetre_coords, values=["NORD DE MAROC 26191", "Sud Maroc 26192", "Sahara Nord 26194", "Sahara Sud 26195", "WGS EPSG 3857"], state="readonly")
    combo_epsg.current(0)
    combo_epsg.grid(row=3, column=1)

    tk.Button(fenetre_coords, text="Ajouter Point", command=ajouter_point).grid(row=4, column=0, columnspan=2, pady=5)
    listbox_points = tk.Listbox(fenetre_coords, width=45)
    listbox_points.grid(row=5, column=0, columnspan=2)
    listbox_points.bind("<<ListboxSelect>>", remplir_champs)

    tk.Button(fenetre_coords, text="Modifier le point sélectionné", command=modifier_point).grid(row=6, column=0, columnspan=2, pady=2)
    tk.Button(fenetre_coords, text="Supprimer le point sélectionné", command=supprimer_point).grid(row=7, column=0, columnspan=2, pady=2)

    tk.Button(fenetre_coords, text="Afficher sur Carte", command=afficher_points).grid(row=8, column=0, columnspan=2, pady=10)


def generer_carte(*args):
    global gdf, centre
    titre_recherche = champ_titre.get()
    fond = combo_fond.get()
    titre_personnalise = champ_titre_carte.get().strip() or "Carte des Titres Fonciers"

    fonds = {
        "Plan": ("https://www.google.com/maps/vt?lyrs=m@189&gl=ma&x={x}&y={y}&z={z}", "Tiles © GOOGLE MAPS"),
        "Hybrid": ("https://www.google.com/maps/vt?lyrs=y@189&gl=ma&x={x}&y={y}&z={z}", "Tiles © GOOGLE HYBRID"),
        "Satellite": ("https://www.google.com/maps/vt?lyrs=s@189&gl=ma&x={x}&y={y}&z={z}", "Tiles © GOOGLE SAT")
    }

    tiles, attr = fonds.get(fond, ("OpenStreetMap", None))

    if centre:
        centre_map = [centre.y, centre.x]
    elif geojson_gdf is not None and not geojson_gdf.empty:
        centre_geom = geojson_gdf.unary_union.centroid
        centre_map = [centre_geom.y, centre_geom.x]
    else:
        centre_map = [33.5899, -7.6039]

    carte = folium.Map(location=centre_map, zoom_start=15, tiles=tiles, attr=attr,
                       control_scale=True, min_zoom=2, max_zoom=22)

    if gdf is not None and titres_active:
        for _, row in gdf.iterrows():
            folium.GeoJson(row["geometry"], tooltip=f"Titre : {row['num']}", style_function=lambda x: {'color': 'blue'}).add_to(carte)

    if geojson_gdf is not None:
        for i, row in geojson_gdf.iterrows():
            folium.GeoJson(
                row["geometry"],
                tooltip=f"GeoJSON ID: {i+1}",
                style_function=lambda x: {
                    'color': 'green',
                    'weight': 3,
                    'fillOpacity': 0.4
                }
            ).add_to(carte)

        if gdf is not None:
            titres_proj = gdf.to_crs(epsg=32629)
            geojson_proj = geojson_gdf.to_crs(epsg=32629)
            for i, geojson_row in geojson_proj.iterrows():
                for j, titre_row in titres_proj.iterrows():
                    intersection = geojson_row.geometry.intersection(titre_row.geometry)
                    if not intersection.is_empty:
                        intersection_wgs84 = gpd.GeoSeries([intersection], crs="EPSG:32629").to_crs(epsg=4326).iloc[0]
                        folium.GeoJson(
                            intersection_wgs84,
                            style_function=lambda x: {
                                'color': 'orange',
                                'weight': 3,
                                'fillOpacity': 0.6
                            },
                            tooltip="Intersection"
                        ).add_to(carte)

    if gdf is not None and titre_recherche:
        match = gdf[gdf["num"].astype(str) == titre_recherche]
        if not match.empty:
            union_geom = unary_union(match.geometry)
            centroid = union_geom.centroid
            minx, miny, maxx, maxy = union_geom.bounds
            carte.fit_bounds([(miny, minx), (maxy, maxx)], padding=(20, 20))
            match_proj = match.to_crs(epsg=32629)
            surface_totale = match_proj.geometry.area.sum()
            folium.GeoJson(union_geom, style_function=lambda x: {'color': 'red'}).add_to(carte)
            popup_content = f"Titre : {titre_recherche}<br>Surface : {surface_totale:.2f} m²"
            folium.Marker([centroid.y, centroid.x], popup=popup_content, icon=folium.Icon(color="red")).add_to(carte)

    # Ajout du titre sur la carte
    titre_html = f"""
    <div style="position: fixed; top: 10px; left: 50%;
                transform: translateX(-50%);
                background-color: white;
                padding: 8px 25px;
                border: 3px solid black;
                font-size: 22px;
                font-weight: bold;
                font-family: Arial, sans-serif;
                color: darkblue;
                z-index:9999;">
        {titre_personnalise}
    </div>
    """
    carte.get_root().html.add_child(folium.Element(titre_html))

    # ✅ Ajout de l'outil de mesurage (distance et surface)
    carte.add_child(MeasureControl(
        primary_length_unit='meters',
        secondary_length_unit='kilometers',
        primary_area_unit='sqmeters',
        secondary_area_unit='hectares',
        position='topright',
        active_color='red',
        completed_color='green'
    ))

    # Export HTML et ouverture
    carte.save("carte_recherche.html")
    webbrowser.open("file://" + os.path.abspath("carte_recherche.html"))

    # ✅ Ajout de l'outil de mesurage (distance et surface)
    carte.add_child(MeasureControl(
        primary_length_unit='meters',
        secondary_length_unit='kilometers',
        primary_area_unit='sqmeters',
        secondary_area_unit='hectares',
        position='topright',
        active_color='red',
        completed_color='green'
    ))

    # Export HTML et ouverture
    carte.save("carte_recherche.html")
    webbrowser.open("file://" + os.path.abspath("carte_recherche.html"))

def toggle_titres():
    global titres_active
    titres_active = not titres_active
    btn_toggle.config(text="Désactiver les titres" if titres_active else "Activer les titres")

def exporter_png():
    messagebox.showinfo("Export", "📌 Ajustez le zoom dans la carte HTML, puis cliquez sur OK.")
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--window-size=1200,1000")
    driver = webdriver.Chrome(options=chrome_options)
    chemin_html = os.path.abspath("carte_recherche.html")
    driver.get("file://" + chemin_html)
    messagebox.showinfo("Capture", "Quand la carte est prête, cliquez sur OK.")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    nom_base = f"carte_{timestamp}"
    dossier = "exports"
    os.makedirs(dossier, exist_ok=True)
    chemin_png = os.path.join(dossier, nom_base + ".png")
    driver.save_screenshot(chemin_png)
    image = Image.open(chemin_png)
    image.save(os.path.join(dossier, nom_base + ".tiff"))
    image.save(os.path.join(dossier, nom_base + ".pdf"))
    messagebox.showinfo("Export terminé", f"✅ Exporté dans : {dossier}")
def exporter_coordonnees_geojson():
    if geojson_gdf is None or geojson_gdf.empty:
        messagebox.showwarning("Aucun GeoJSON", "Aucune coordonnée locale ou forme chargée.")
        return
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        chemin = f"coordonnees_locales_{timestamp}.geojson"
        geojson_gdf.to_file(chemin, driver="GeoJSON")
        messagebox.showinfo("Export terminé", f"Coordonnées locales exportées vers {chemin}")
        os.startfile(chemin)
    except Exception as e:
        messagebox.showerror("Erreur export", f"Erreur lors de l'export : {e}")


def exporter_intersections_geojson():
    if gdf is None or geojson_gdf is None:
        messagebox.showwarning("Données manquantes", "Chargez une ville et un GeoJSON.")
        return
    try:
        titres_proj = gdf.to_crs(epsg=32629)
        geojson_proj = geojson_gdf.to_crs(epsg=32629)

        intersections = []

        for geojson_row in geojson_proj.geometry:
            for titre_row in titres_proj.geometry:
                inter = geojson_row.intersection(titre_row)
                if not inter.is_empty:
                    intersections.append(inter)

        if not intersections:
            messagebox.showinfo("Aucune intersection", "Aucune géométrie d'intersection trouvée.")
            return

        gdf_inter = gpd.GeoDataFrame(geometry=intersections, crs="EPSG:32629").to_crs(epsg=4326)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        chemin = f"intersections_{timestamp}.geojson"
        gdf_inter.to_file(chemin, driver="GeoJSON")
        messagebox.showinfo("Export terminé", f"Intersections exportées vers {chemin}")
        os.startfile(chemin)
    except Exception as e:
        messagebox.showerror("Erreur export", f"Erreur lors de l'export : {e}")


def generer_carte(*args):
    global gdf, centre
    titre_recherche = champ_titre.get()
    fond = combo_fond.get()
    titre_personnalise = champ_titre_carte.get().strip() or "Carte des Titres Fonciers"

    fonds = {
        "Plan": ("https://www.google.com/maps/vt?lyrs=m@189&gl=ma&x={x}&y={y}&z={z}", "Tiles © GOOGLE MAPS"),
        "Hybrid": ("https://www.google.com/maps/vt?lyrs=y@189&gl=ma&x={x}&y={y}&z={z}", "Tiles © GOOGLE HYBRID"),
        "Satellite": ("https://www.google.com/maps/vt?lyrs=s@189&gl=ma&x={x}&y={y}&z={z}", "Tiles © GOOGLE SAT")
    }

    tiles, attr = fonds.get(fond, ("OpenStreetMap", None))

    if centre:
        centre_map = [centre.y, centre.x]
    elif geojson_gdf is not None and not geojson_gdf.empty:
        centre_geom = geojson_gdf.unary_union.centroid
        centre_map = [centre_geom.y, centre_geom.x]
    else:
        centre_map = [33.5899, -7.6039]

    carte = folium.Map(location=centre_map, zoom_start=15, tiles=tiles, attr=attr,
                       control_scale=True, min_zoom=2, max_zoom=22)

    if gdf is not None and titres_active:
        for _, row in gdf.iterrows():
            folium.GeoJson(row["geometry"], tooltip=f"Titre : {row['num']}", style_function=lambda x: {'color': 'blue'}).add_to(carte)

    if geojson_gdf is not None:
        for i, row in geojson_gdf.iterrows():
            folium.GeoJson(
                row["geometry"],
                tooltip=f"GeoJSON ID: {i+1}",
                style_function=lambda x: {
                    'color': 'green',
                    'weight': 3,
                    'fillOpacity': 0.4
                }
            ).add_to(carte)

        if gdf is not None:
            titres_proj = gdf.to_crs(epsg=32629)
            geojson_proj = geojson_gdf.to_crs(epsg=32629)
            for i, geojson_row in geojson_proj.iterrows():
                for j, titre_row in titres_proj.iterrows():
                    intersection = geojson_row.geometry.intersection(titre_row.geometry)
                    if not intersection.is_empty:
                        intersection_wgs84 = gpd.GeoSeries([intersection], crs="EPSG:32629").to_crs(epsg=4326).iloc[0]
                        folium.GeoJson(
                            intersection_wgs84,
                            style_function=lambda x: {
                                'color': 'orange',
                                'weight': 3,
                                'fillOpacity': 0.6
                            },
                            tooltip="Intersection"
                        ).add_to(carte)

    if gdf is not None and titre_recherche:
        match = gdf[gdf["TITRE"].astype(str) == titre_recherche]
        if not match.empty:
            union_geom = unary_union(match.geometry)
            centroid = union_geom.centroid
            minx, miny, maxx, maxy = union_geom.bounds
            carte.fit_bounds([(miny, minx), (maxy, maxx)], padding=(20, 20))
            match_proj = match.to_crs(epsg=32629)
            surface_totale = match_proj.geometry.area.sum()
            folium.GeoJson(union_geom, style_function=lambda x: {'color': 'red'}).add_to(carte)
            popup_content = f"Titre : {titre_recherche}<br>Surface : {surface_totale:.2f} m²"
            folium.Marker([centroid.y, centroid.x], popup=popup_content, icon=folium.Icon(color="red")).add_to(carte)

    # Ajout du titre sur la carte
    titre_html = f"""
    <div style="position: fixed; top: 10px; left: 50%;
                transform: translateX(-50%);
                background-color: white;
                padding: 8px 25px;
                border: 3px solid black;
                font-size: 22px;
                font-weight: bold;
                font-family: Arial, sans-serif;
                color: darkblue;
                z-index:9999;">
        {titre_personnalise}
    </div>
    """
    carte.get_root().html.add_child(folium.Element(titre_html))

    # ✅ Ajout de l'outil de mesurage (distance et surface)
    carte.add_child(MeasureControl(
        primary_length_unit='meters',
        secondary_length_unit='kilometers',
        primary_area_unit='sqmeters',
        secondary_area_unit='hectares',
        position='topright',
        active_color='red',
        completed_color='green'
    ))

    # Export HTML et ouverture
    carte.save("carte_recherche.html")
    webbrowser.open("file://" + os.path.abspath("carte_recherche.html"))

    # ✅ Ajout de l'outil de mesurage (distance et surface)
    carte.add_child(MeasureControl(
        primary_length_unit='meters',
        secondary_length_unit='kilometers',
        primary_area_unit='sqmeters',
        secondary_area_unit='hectares',
        position='topright',
        active_color='red',
        completed_color='green'
    ))

    # Export HTML et ouverture
    carte.save("carte_recherche.html")
    webbrowser.open("file://" + os.path.abspath("carte_recherche.html"))

def toggle_titres():
    global titres_active
    titres_active = not titres_active
    btn_toggle.config(text="Désactiver les titres" if titres_active else "Activer les titres")

def exporter_png():
    messagebox.showinfo("Export", "📌 Ajustez le zoom dans la carte HTML, puis cliquez sur OK.")
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--window-size=1200,1000")
    driver = webdriver.Chrome(options=chrome_options)
    chemin_html = os.path.abspath("carte_recherche.html")
    driver.get("file://" + chemin_html)
    messagebox.showinfo("Capture", "Quand la carte est prête, cliquez sur OK.")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    nom_base = f"carte_{timestamp}"
    dossier = "exports"
    os.makedirs(dossier, exist_ok=True)
    chemin_png = os.path.join(dossier, nom_base + ".png")
    driver.save_screenshot(chemin_png)
    image = Image.open(chemin_png)
    image.save(os.path.join(dossier, nom_base + ".tiff"))
    image.save(os.path.join(dossier, nom_base + ".pdf"))
    messagebox.showinfo("Export terminé", f"✅ Exporté dans : {dossier}")

# Interface principale
fenetre = tk.Tk()
fenetre.title("Application Géospatiale Complète")
fenetre.geometry("430x720")
frame = tk.Frame(fenetre, bg="#f0f0f0")
frame.pack(padx=10, pady=10, fill="both", expand=True)

tk.Label(frame, text="Choisir la ville :", font=("Arial", 12), bg="#f0f0f0").pack()
combo_ville = ttk.Combobox(frame, values=charger_villes(), font=("Arial", 12), width=25)
combo_ville.pack(pady=5)
combo_ville.bind("<<ComboboxSelected>>", lambda e: charger_donnees(combo_ville.get()))

tk.Label(frame, text="Numéro du titre :", font=("Arial", 12), bg="#f0f0f0").pack()
champ_titre = tk.Entry(frame, font=("Arial", 12))
champ_titre.pack(pady=5)

tk.Label(frame, text="Titre de la carte :", font=("Arial", 12), bg="#f0f0f0").pack()
champ_titre_carte = tk.Entry(frame, font=("Arial", 12))
champ_titre_carte.pack(pady=5)

tk.Label(frame, text="Fond de carte :", font=("Arial", 12), bg="#f0f0f0").pack()
combo_fond = ttk.Combobox(frame, values=["Plan", "Satellite", "Hybrid"], font=("Arial", 12))
combo_fond.current(0)
combo_fond.pack(pady=5)

tk.Button(frame, text="Générer la carte", font=("Arial", 12), bg="#4CAF50", fg="white", command=generer_carte).pack(pady=10)
btn_toggle = tk.Button(frame, text="Désactiver les titres", font=("Arial", 12), bg="#FF5733", fg="white", command=toggle_titres)
btn_toggle.pack(pady=5)

tk.Button(frame, text="Exporter PNG/TIFF/PDF", font=("Arial", 12), bg="#2196F3", fg="white", command=exporter_png).pack(pady=5)
tk.Button(frame, text="📁 Charger GeoJSON", font=("Arial", 12), bg="#9C27B0", fg="white", command=charger_geojson).pack(pady=5)
tk.Button(frame, text="📊 Intersection & Export", font=("Arial", 12), bg="#FF9800", fg="white", command=analyser_intersection).pack(pady=5)
tk.Button(frame, text="📍 Ajouter coordonnées locales", font=("Arial", 12), bg="#795548", fg="white", command=ajouter_coordonnees_locales).pack(pady=5)
tk.Button(frame, text="💾 Export Coordonnées GeoJSON", font=("Arial", 12), bg="#4CAF50", fg="white", command=exporter_coordonnees_geojson).pack(pady=5)
tk.Button(frame, text="💾 Export Intersections GeoJSON", font=("Arial", 12), bg="#E91E63", fg="white", command=exporter_intersections_geojson).pack(pady=5)
tk.Button(frame, text="📁 Charger GeoJSON (multi)", font=("Arial", 12), bg="#9C27B0", fg="white", command=charger_geojson).pack(pady=5)
tk.Button(frame, text="🔁 Intersection GeoJSON↔GeoJSON", font=("Arial", 12), bg="#03A9F4", fg="white", command=analyser_intersection_geojson_geojson).pack(pady=5)

fenetre.mainloop()
# --- Fonctions pour chaque couche ---
def toggle_titres():
    global titres_active
    titres_active = not titres_active
    btn_toggle.config(text="Désactiver les titres" if titres_active else "Activer les titres")


def toggle_geojson():
    global geojson_active
    geojson_active = not geojson_active
    btn_toggle_geojson.config(text="Désactiver GeoJSON" if geojson_active else "Activer GeoJSON")


def toggle_intersections():
    global intersections_active
    intersections_active = not intersections_active
    btn_toggle_intersection.config(
        text="Désactiver Intersections" if intersections_active else "Activer Intersections")


# --- Fonction centrale : basculer couche de travail ---
def toggle_couche_travail():
    global titres_active, geojson_active, intersections_active, couche_travail_active

    if couche_travail_active == "titres":
        titres_active = not titres_active
        message = "✅ Titres activés" if titres_active else "❌ Titres désactivés"

    elif couche_travail_active == "geojson":
        geojson_active = not geojson_active
        message = "✅ GeoJSON activés" if geojson_active else "❌ GeoJSON désactivés"

    elif couche_travail_active == "intersection":
        intersections_active = not intersections_active
        message = "✅ Intersections activées" if intersections_active else "❌ Intersections désactivées"

    else:
        message = "Aucune couche de travail sélectionnée."

    messagebox.showinfo("Couches", f"{message}\n📌 Regénérez la carte pour voir le changement.")


# --- Exemple de mise à jour de la couche active dans d'autres fonctions ---
# Dans charger_donnees() ou generer_carte() lorsque titres sont affichés :
# global couche_travail_active
# couche_travail_active = "titres"

# Dans afficher_points() (coordonnées locales) :
# global couche_travail_active
# couche_travail_active = "geojson"

# Dans analyser_intersection() :
# global couche_travail_active
# couche_travail_active = "intersection"


# --- Boutons dans l'interface graphique principale (Tkinter) ---
btn_toggle = tk.Button(frame, text="Désactiver les titres", font=("Arial", 12), bg="#FF5733", fg="white", command=toggle_titres)
btn_toggle.pack(pady=5)

btn_toggle_geojson = tk.Button(frame, text="Désactiver GeoJSON", font=("Arial", 12), bg="#607D8B", fg="white", command=toggle_geojson)
btn_toggle_geojson.pack(pady=5)

btn_toggle_intersection = tk.Button(frame, text="Désactiver Intersections", font=("Arial", 12), bg="#3F51B5", fg="white", command=toggle_intersections)
btn_toggle_intersection.pack(pady=5)

tk.Button(frame, text="🌓 Afficher / Cacher couche de travail", font=("Arial", 12), bg="#9E9E9E", fg="white", command=toggle_couche_travail).pack(pady=5)
tk.Button(frame, text="💾 Export Coordonnées GeoJSON", font=("Arial", 12), bg="#4CAF50", fg="white", command=exporter_coordonnees_geojson).pack(pady=5)
tk.Button(frame, text="💾 Export Intersections GeoJSON", font=("Arial", 12), bg="#E91E63", fg="white", command=exporter_intersections_geojson).pack(pady=5)



# --- Dans la fonction generer_carte() ---
# Remplacer les blocs par ceux-ci pour respecter les couches actives :

# Titres :
# if gdf is not None and titres_active:
#     for _, row in gdf.iterrows():
#         folium.GeoJson(row["geometry"], tooltip=f"Titre : {row['num']}", style_function=lambda x: {'color': 'blue'}).add_to(carte)

# GeoJSON :
# if geojson_gdf is not None and geojson_active:
#     for i, row in geojson_gdf.iterrows():
#         folium.GeoJson(
#             row["geometry"],
#             tooltip=f"GeoJSON ID: {i+1}",
#             style_function=lambda x: {
#                 'color': 'green',
#                 'weight': 3,
#                 'fillOpacity': 0.4
#             }
#         ).add_to(carte)

# Intersections :
# if gdf is not None and geojson_gdf is not None and intersections_active:
#     titres_proj = gdf.to_crs(epsg=32629)
#     geojson_proj = geojson_gdf.to_crs(epsg=32629)
#     for i, geojson_row in geojson_proj.iterrows():
#         for j, titre_row in titres_proj.iterrows():
#             intersection = geojson_row.geometry.intersection(titre_row.geometry)
#             if not intersection.is_empty:
#                 intersection_wgs84 = gpd.GeoSeries([intersection], crs="EPSG:32629").to_crs(epsg=4326).iloc[0]
#                 folium.GeoJson(
#                     intersection_wgs84,
#                     style_function=lambda x: {
#                         'color': 'orange',
#                         'weight': 3,
#                         'fillOpacity': 0.6
#                     },
#                     tooltip="Intersection"
#                 ).add_to(carte)
