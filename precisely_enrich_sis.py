import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry import Point
from snowflake.snowpark.context import get_active_session
import streamlit as st
import pydeck as pdk
#import plotly.express as px
#import altair as alt

# -- Page Configuration
st.set_page_config(
    page_title="MBI Spatial Insights Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- Custom CSS for Professional Styling
st.markdown(
    """
    <style>
    :root {
      /* Brand palette */
      --clr-primary: #274872;      /* dark blue */
      --clr-secondary: #b84dff;    /* medium blue */
      --clr-accent: #FF4081;       /* pink accent */
      --clr-bg-light: #f3f6fa;     /* off-white */
      --clr-bg-gradient: #e3eaf1;  /* light gradient end */
      --clr-text: #2c3e50;         /* dark slate */
      --clr-text-white: #FFFFFF;
    }
    /* Sidebar background and text */
    section[data-testid="stSidebar"] {
        background-color: var(--clr-primary) !important;
        color: #fff !important;
    }
    /* Sidebar label and select label */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .css-1c7y2kd, /* Selectbox label */
    section[data-testid="stSidebar"] .css-1kyxreq, /* Slider label */
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span
    {
        color: #44a3cf !important;
    }
    /* Text input label */
    section[data-testid="stSidebar"] .stTextInput label {
        color: #fff !important;
    }
    /* Selectbox text color */
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #fff !important;
    }
    /* Slider label */
    section[data-testid="stSidebar"] .stSlider label {
        color: #fff !important;
    }
    
section[data-testid="stSidebar"] .stButton>button {
    background-color: #274872 !important;         /* Solid blue */
    color: #fff !important;                       /* White text */
    border: 1px solid #274872 !important;         /* Blue border */
    border-radius: 6px !important;                /* Rounded corners */
    font-weight: 600 !important;
    width: 100%;
    padding: 0.5rem 0.2rem;
    margin-top: 0.5rem;
    box-shadow: none !important;
    transition: background 0.2s, color 0.2s, border 0.2s;
    outline: none !important;
    text-shadow: none !important;
    -webkit-text-fill-color: #fff !important;     /* Always show label */
}

/* On hover, make it a lighter blue */
section[data-testid="stSidebar"] .stButton>button:hover:not(:disabled),
section[data-testid="stSidebar"] .stButton>button:focus:not(:disabled) {
    background-color: #3a5998 !important;         /* Lighter blue */
    color: #fff !important;
    border: 1px solid #3a5998 !important;
    -webkit-text-fill-color: #fff !important;
}

/* Disabled button */
section[data-testid="stSidebar"] .stButton>button:disabled {
    background-color: #aac1de !important;         /* Muted blue */
    color: #f3f6fa !important;
    border: 1px solid #aac1de !important;
    -webkit-text-fill-color: #f3f6fa !important;
}



    
    /* App background */
    .stApp {
        background: linear-gradient(135deg, var(--clr-bg-light) 70%, var(--clr-bg-gradient) 100%);
        color: var(--clr-text);
        font-family: "Segoe UI", Tahoma, sans-serif;
    }
    /* Header bar */
    header .css-1v3fvcr.e1fqkh3o2 {
      background-color: var(--clr-primary);
      padding: 0.75rem 2rem;
      margin-bottom: 1.5rem;
    }
    header h1 {
      color: white !important;
      font-size: 2rem !important;
      font-weight: 700 !important;
      margin: 0;
    }
    /* Title & subtitle */
    .title {
        color: var(--clr-primary);
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        color: var(--clr-primary);
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background-color: var(--clr-primary) !important;
        padding: 1rem;
    }
    .stSidebar .stTextInput>div>div>input
    {
        background-color: white;
    },
    .stSidebar .stSelectbox>div>div>div>input,
    .stSidebar .stSlider>div>div>div>input {
        border-radius: 8px !important;
        padding: 0.5rem !important;
        background-color: white !important;
        color: var(--clr-text) !important;
    }

    /* Main container cards */
    .block-container {
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 2px 8px rgba(44, 62, 80, 0.1);
        background-color: white;
    }
    /* Dataframe styling */
    .stDataFrame table {
      border-collapse: collapse;
    }
    .stDataFrame th, .stDataFrame td {
      padding: 0.5rem;
    }
.block-container {
    background: #fff;
    border-radius: 14px;
    box-shadow: 0 3px 14px 0 rgba(44, 62, 80, 0.12);
    padding: 0 0 1.5rem 0;
    margin-bottom: 1.5rem;
}
.card-header {
    border-radius: 14px 14px 0 0;
    background: #274872;
    color: #fff;
    font-size: 1.22rem;
    font-weight: bold;
    padding: 1rem 1.2rem;
    display: flex;
    align-items: center;
    margin-bottom: 0;
}
.header-green {
    background: #238347;
}
.header-blue {
    background: #274872;
}
.card-header .icon {
    margin-right: 0.7rem;
    font-size: 1.2rem;
}
.card-content {
    padding: 1.2rem 1.4rem 0.5rem 1.4rem;
}

    
    </style>
    """,
    unsafe_allow_html=True,
)

# -- Sidebar: Filter Controls
with st.sidebar.form(key="filter_form"):
    st.markdown("## 🔍 Filters", unsafe_allow_html=True)
    microcode = st.text_input(
        "MICROCODE", value="13123031007", max_chars=20,
        help="Enter a MICROCODE (e.g., 13123031007)"
    )
    layer_choice = st.selectbox(
        "Data Layers", ["Both", "Demographics Polygons", "POI Points"]
    )
    opacity = st.slider(
        "Layer Opacity", min_value=10, max_value=100, value=30, step=5,
        help="Adjust fill opacity for polygon layer"
    )
    radius = st.slider(
        "Point Radius", min_value=1, max_value=20, value=6,
        help="Adjust marker size for POI points"
    )
    apply = st.form_submit_button(label="Apply Filter 🔍")

# Active session
session = get_active_session()

@st.cache_data(show_spinner="Loading data...", ttl=600)
def load_data(microcode):
    q_poly = f'''
        SELECT * FROM MBI__PREMIUM_GEOSPATIAL__MARKET_DATA.PROMOTIONAL."mbi_demographics_jp" 
        WHERE MICROCODE = '{microcode}'
    '''
    df_poly = session.sql(q_poly).to_pandas()
    df_poly['GEOM'] = df_poly.apply(create_geom, axis=1)
    gdf_polygons = gpd.GeoDataFrame(df_poly, geometry='GEOM', crs="EPSG:4326")

    q_point = f'''
        SELECT * FROM MBI__PREMIUM_GEOSPATIAL__MARKET_DATA.PROMOTIONAL."poi_jp" 
        WHERE MICROCODE = '{microcode}'
    '''
    df_point = session.sql(q_point).to_pandas()
    df_point['LATITUDE'] = df_point['LATITUDE'].astype(float)
    df_point['LONGITUDE'] = df_point['LONGITUDE'].astype(float)
    df_point['GEOM'] = df_point.apply(create_geom, axis=1)
    gdf_points = gpd.GeoDataFrame(df_point, geometry='GEOM', crs="EPSG:4326")

    return gdf_polygons, gdf_points

def create_geom(row):
    if 'WKT' in row and pd.notnull(row['WKT']):
        return wkt.loads(row['WKT'])
    else:
        return Point(row['LONGITUDE'], row['LATITUDE'])

def get_polygon_coords(geom):
    if geom.geom_type == 'Polygon':
        return [list(geom.exterior.coords)]
    elif geom.geom_type == 'MultiPolygon':
        return [list(p.exterior.coords) for p in geom.geoms]
    else:
        return None

def render_combined_map(gdf_points, gdf_polygons):
    # Polygon layer
    df_poly_layer = pd.DataFrame(gdf_polygons.drop(columns=['GEOM']))
    df_poly_layer['coordinates'] = gdf_polygons['GEOM'].apply(get_polygon_coords)

    polygon_layer = pdk.Layer(
        'PolygonLayer',
        df_poly_layer,
        get_polygon='coordinates',
        stroked=True,
        extruded=False,
        opacity=0.3,
        filled=True,
        get_fill_color=[52, 102, 168, 120], # angular blue
        get_line_color=[44, 62, 80],
        pickable=True
    )

    point_layer = pdk.Layer(
        "ScatterplotLayer",
        gdf_points,
        get_position=["LONGITUDE", "LATITUDE"],
        get_color=[255, 64, 129, 200],
        get_radius=0.5,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=6,
        radius_min_pixels=2,
        radius_max_pixels=80,
        line_width_min_pixels=2,
    )

    point_lat = gdf_points['LATITUDE'].mean()
    point_lon = gdf_points['LONGITUDE'].mean()

    gdf_poly_proj = gdf_polygons.to_crs(epsg=3857)
    poly_centroids_proj = gdf_poly_proj.centroid
    poly_centroids = poly_centroids_proj.to_crs(epsg=4326)
    poly_lat = poly_centroids.y.mean() if not poly_centroids.empty else point_lat
    poly_lon = poly_centroids.x.mean() if not poly_centroids.empty else point_lon

    combined_lat = (point_lat + poly_lat) / 2 if not pd.isnull(poly_lat) else point_lat
    combined_lon = (point_lon + poly_lon) / 2 if not pd.isnull(poly_lon) else point_lon

    view_state = pdk.ViewState(
        latitude=combined_lat,
        longitude=combined_lon,
        zoom=15,
        bearing=0,
        pitch=0
    )

    tooltip = {
        'html': '''
                <div style="font-size:13px;">
                <b>Name:</b> {NAME}<br>
                <b>Microcode:</b> {MICROCODE}<br>
                <b>Households (total):</b> {HH_T}<br>
                <b>Avg. Household Size:</b> {HH_SIZE}<br>
                <b>Population (Males):</b> {MALE}<br>
                <b>Population (Females):</b> {FEMALE}<br>
                <b>Population (University):</b> {EDU_5}<br>
                <b>Purchasing Power:</b> {PP_EURO} <br>
                <b>Address:</b> {MAIN_ADDRE}<br>
                <b>Post Code:</b> {POSTCODE}<br>
                <b>Main Class:</b> {MAIN_CLASS}<br>
                <b>Business:</b> {BUSINESS_L}<br>
                <b>Group Name:</b> {GROUP_NAME}<br>
                </div>
            ''',
        'style': {
            'backgroundColor': '#3266a8',
            'color': 'white'
        }
    }

    deck = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        layers=[polygon_layer, point_layer],
        initial_view_state=view_state,
        tooltip=tooltip
    )
    return deck


def render_map(polygons, points, opacity_val, radius_val):
    # Polygon layer
    df_poly = pd.DataFrame(polygons.drop(columns=['GEOM']))
    df_poly['coords'] = polygons['GEOM'].apply(get_polygon_coords)
    poly_layer = pdk.Layer(
        'PolygonLayer',
        df_poly,
        get_polygon='coords',
        filled=True,
        stroked=True,
        opacity=opacity_val / 100,
        get_fill_color=[52, 102, 168, int(opacity_val * 2.55)],
        get_line_color=[44, 62, 80]
    )

    # Point layer
    point_layer = pdk.Layer(
        'ScatterplotLayer',
        points,
        get_position=['LONGITUDE', 'LATITUDE'],
        get_fill_color=[255, 64, 129, 200],  # var(--clr-accent)
        # keep the raw data radius = 1, then scale it by the slider
        get_radius=1,
        radius_scale=radius_val,
        radius_min_pixels=2,
        radius_max_pixels=80,
        pickable=True
    )

    # Combine data for centering
    all_lats = list(points['LATITUDE']) + [c[1] for coords in df_poly['coords'] for c in coords[0]]
    all_lons = list(points['LONGITUDE']) + [c[0] for coords in df_poly['coords'] for c in coords[0]]
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)

    view = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=14,
        bearing=0,
        pitch=0
    )

    tooltip = {
        'html': '''
                <div style="font-size:13px;">
                <b>Name:</b> {NAME}<br>
                <b>Microcode:</b> {MICROCODE}<br>
                <b>Households (total):</b> {HH_T}<br>
                <b>Avg. Household Size:</b> {HH_SIZE}<br>
                <b>Population (Males):</b> {MALE}<br>
                <b>Population (Females):</b> {FEMALE}<br>
                <b>Population (University):</b> {EDU_5}<br>
                <b>Purchasing Power:</b> {PP_EURO} <br>
                <b>Address:</b> {MAIN_ADDRE}<br>
                <b>Post Code:</b> {POSTCODE}<br>
                <b>Main Class:</b> {MAIN_CLASS}<br>
                <b>Business:</b> {BUSINESS_L}<br>
                <b>Group Name:</b> {GROUP_NAME}<br>
                </div>
            ''',
        'style': {
            'backgroundColor': '#3266a8',
            'color': 'white'
        }
    }

    layers = []
    if layer_choice in ['Both', 'Demographics Polygons']:
        layers.append(poly_layer)
    if layer_choice in ['Both', 'POI Points']:
        layers.append(point_layer)

    return pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        layers=layers,
        initial_view_state=view,
        tooltip=tooltip,
    )

# -- Main App Content
st.markdown('<div class="title">MBI Spatial Insights Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Visualize demographic & POI data interactively</div>', unsafe_allow_html=True)

if apply:
    with st.spinner("Fetching and rendering data..."):
        gdf_polygons, gdf_points = load_data(microcode)
        if gdf_polygons.empty and gdf_points.empty:
            st.warning(f"No data found for MICROCODE: {microcode}")
        else:
            st.subheader(f"Results for MICROCODE: {microcode}")
            col1, col2 = st.columns([3, 1])
            # --- Map Card ---
            with col1:
                #st.markdown('<div class="block-container">', unsafe_allow_html=True)
                st.markdown(
                    '<div class="card-header header-blue">'
                    '<span class="icon">🗺️</span> Map Display'
                    '</div>',
                    unsafe_allow_html=True
                )
                st.markdown('<div class="card-content">', unsafe_allow_html=True)
                st.pydeck_chart(render_map(gdf_polygons, gdf_points, opacity, radius))
                st.markdown('</div>', unsafe_allow_html=True)  # end card-content
                st.markdown('</div>', unsafe_allow_html=True)  # end block-container

            # --- Attributes Card ---
            with col2:
                #st.markdown('<div class="block-container">', unsafe_allow_html=True)
                st.markdown(
                    '<div class="card-header header-green">'
                    '<span class="icon">📋</span> Attributes'
                    '</div>',
                    unsafe_allow_html=True
                )
                st.markdown('<div class="card-content">', unsafe_allow_html=True)
                st.write("**Polygons:**", len(gdf_polygons))
                st.write("**Points:**", len(gdf_points))


               # st.dataframe(gdf_points["MAIN_CLASS"], use_container_width=True)
                #st.dataframe(gdf_points.head(), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)  # end card-content
                st.markdown('</div>', unsafe_allow_html=True)  # end block-container
else:
    st.info("Enter a MICROCODE and click Apply Filter to begin.")
