import folium
m=folium.Map(location=[28.61, 77.23], zoom_start=5)
folium.Marker([28.61, 77.23],  popup="New Delhi").add_to(m)
m.save("map1.html")
m