import matplotlib.pyplot as plt
import string
from pprint import pprint
from bisect import bisect_left, insort


coord = [[12, 14], [10, 13], [9, 16], [7, 14], [5, 16], [4, 12], 
         [3, 13], [2, 7], [4, 8], [3, 2], [5, 4], [7, 2], 
         [8, 5], [10, 4], [10, 9]]
coord.append(coord[0]) # Powtórzenie ostatniego punktu by zamknąć figurę

labels = list(string.ascii_uppercase)
helper_dict = {}
diagonals = []


# Stworzenie obrazu wielokąta
def generate_image():
  xs, ys = zip(*coord) # Stworzenie listy x i y

  plt.figure(plt.figure(figsize=(10, 8)))
  plt.plot(xs, ys, 'b-', linewidth= 2) 

  # Wygenerowanie podpisów dla punktów
  for i, (x, y) in enumerate(coord[:-1]):
    plt.annotate(labels[i], (x, y), textcoords="offset points", xytext=(0,7), ha='center',
                fontsize=12, fontweight='bold', color='navy')
    
  vertex_coords = generate_dict(coord)

  # Rysowanie przekątnych
  for v1, v2 in diagonals:
    x1, y1 = vertex_coords[v1]
    x2, y2 = vertex_coords[v2]
    plt.plot([x1, x2], [y1, y2], 'r--', linewidth= 1.5)
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    plt.annotate(f"{v1}-{v2}", (mid_x, mid_y), fontsize=10, 
                 color='red', bbox=dict(boxstyle="round,pad=0.3", 
                                        fc="white", ec="red", alpha=0.7))
  plt.axis('equal')  
  plt.title("Wielokąt z przekątnymi y-monotonicznymi")
  plt.grid(True, linestyle='--', alpha=0.7)

  plt.show() 

# Utworzenie słownika punktów
def generate_dict(coords):
  dict_of_points = {}
  for i, (x, y) in enumerate(coords[:-1]):
    dict_of_points[labels[i]] = (x, y)
  return dict_of_points

# Funkcje sprawdzające czy punkt jest powyżej, czy poniżej drugiego punktu
def is_above(a, b):
  return a[1] > b[1]
def is_below(a, b):
  return a[1] < b[1]

# Funkcja sprawdzająca, czy punkt leży na prawo, lewo od poprzednich 2 lub jest współliniowy
# det(a, b, c) = ax*by + bx*cy + cx*ay - cx*by - ax*cy - bx*ay
def count_det(a, b, c):
  det = a[0] * b[1] + b[0] * c[1] + c[0] * a[1] - c[0] * b[1] - a[0] * c[1] - b[0] * a[1]
  return det

# Klasyfikacja wierzchołków
def classify_vertices(coords):
  n = len(coords) - 1
  types = []
  dict_of_types = {
    # 'A': 'end'
    # 'B': 'split'
  }
  for i in range(n):
    if i == 0:
      prev = coords[-2]
    else:
      prev = coords[i - 1]
    curr = coords[i]
    next = coords[(i + 1) % n]

    # Sprawdzenie czy poprzedni/następny był powyżej/poniżej
    above_prev = is_above(prev, curr)
    above_next = is_above(next, curr)
    below_prev = is_below(prev, curr)
    below_next = is_below(next, curr)

    # Wyliczamy det, by sprawdzić, czy kąt jest większy/mniejszy/równy 180 stopni
    det = count_det(prev, curr, next)
    # Wyliczamy, czy kąt jest wypukły (mniejszy niż 180 stopni)
    is_convex = det > 0 

    '''
    Początkowy: below_prev, below_next, is_convex
    Dzielący: below_prev, below_next, not is_convex
    Końcowy: above_prev, above_next, is_convex
    Łączący: above_prev, above_next, not is_convex
    Prawidłowy: else
    '''
    if below_prev and below_next:
      if is_convex:
        types.append('start')
      else:
        types.append('split')
    elif above_prev and above_next:
      if is_convex:
        types.append('end')
      else: 
        types.append('merge')
    else:
      types.append('regular')
  for i, type in enumerate(types):
    dict_of_types[labels[i]] = type
  return dict_of_types

# Kolejka priorytetowa
def priority_queue(coords):
  points = generate_dict(coords)
  # pprint(points)
  # for point, value in points.items():
  sorted_items = sorted(points.items(), key=lambda item: (-item[1][1], (item[1][0])))
  return sorted_items

# Drzewo binarne
T = []
def insert_edge(T, x):
  insort(T, x)
  print(f"Dodano wierzchołek {x} do T")

def remove_edge(T, edge_name):
  if edge_name in T:
    T.remove(edge_name)
    print(f"Usunięto wierzchołek {edge_name} z T")

def find_left_edge(T, x):
  if not T:
    print("  T jest pusty")
    return None
  
  x_num = int(x[1:])
  
  # Znajdź wszystkie krawędzie o numerze mniejszym niż x_num
  left_candidates = [e for e in T if int(e[1:]) < x_num]
  
  if left_candidates:
    # Zwróć krawędź o największym numerze spośród tych na lewo
    return max(left_candidates, key=lambda e: int(e[1:]))
  else:
    # Jeśli nie ma krawędzi na lewo, zwróć pierwszą w T (posortowanym numerycznie)
    T_sorted = sorted(T, key=lambda e: int(e[1:]))
    return T_sorted[0]


def find_right_edge(T, x):
  idx = bisect_left(T, x)
  if idx == len(T):
    print("Brak krawędzi po prawej")
    return None
  return T[idx]

# Obsługa typów wierzchołków:
def handle_start_vertex(point, vertices, edges):
  i = vertices[point[0]]
  edge_name = f"e{i}"  
  insert_edge(T, edge_name) # Dodanie punktu do T
  helper_dict[edge_name] = point[0] # Dodanie pomocnika do listy pomocników
  print(f" Pomocnik {edge_name} = {point[0]}")

def handle_end_vertex(point, types, vertices, edges):
  i = vertices[point[0]]
  edge_name = f"e{i-1}"
  helper_vertice = helper_dict.get(edge_name)

  if helper_vertice and types[helper_vertice] == 'merge':
    add_diametral(point[0], helper_vertice)
  remove_edge(T, edge_name)

def handle_split_vertex(point, types, vertices, edges):
  vi = point[0]
  i = vertices[vi] # Index of the vertex vi
  edge_i_name = f"e{i}" # Edge starting at vi

  # 1. Szukaj w T krawędzi ej bezpośrednio na lewo od vi.
  edge_j_name = find_left_edge(T, edge_i_name) # 

  if edge_j_name:
    # 2. Wstaw do D przekątną łączącą vi z pomocnik(ej)
    helper_of_j = helper_dict.get(edge_j_name)
    if helper_of_j:
      add_diametral(vi, helper_of_j)
    # 3. pomocnik(ej) = vi
    helper_dict[edge_j_name] = vi
    print(f" Pomocnik {edge_j_name} = {vi}")
  else:
    print(f"Warning: Nie znaleziono wierzchołka {vi}")
  # 4. Wstaw ei w T i ustaw pomocnik(ei) na vi.
  insert_edge(T, edge_i_name)
  helper_dict[edge_i_name] = vi
  print(f" Pomocnik {edge_j_name} = {vi}")

def handle_merge_vertex(point, types, vertices, edges):
  i = vertices[point[0]]
  edge_name = f"e{i-1}"
  helper_vertice = helper_dict.get(edge_name)

  # Sprawdzamy, czy pomocnik jest wierzchołkiem łączącym
  if helper_vertice and types[helper_vertice] == 'merge':
    add_diametral(point[0], helper_vertice)
  else:
    print(f"Pomocnik {helper_vertice} nie jest łączący")
  # Usunięcie ei - 1 z T
  remove_edge(T, edge_name)
  # Szukaj w T krawędzi ej bezpośrednio na lewo od vi
  vi = point[0]
  edge_left = find_left_edge(T, f"e{i}")
  print(f"Punkt na lewo: {edge_left}")
  if edge_left:
    helper_vertice = helper_dict.get(edge_left)
    if helper_vertice and types[helper_vertice] == 'merge':
      print(f"Pomocnik {helper_vertice} jest łączący")
      add_diametral(point[0], helper_vertice)
  else:
    print(f"Pomocnik {helper_vertice} nie jest łączący")
  helper_dict[edge_left] = point[0]
  print(f" Pomocnik {edge_left} = {point[0]}")

def handle_regular_vertex(point, types, vertices, edges):
  vi = point[0]
  i = vertices[vi]
  n = len(coord) - 1  

  prev_vertex = labels[(labels.index(vi) - 1) % n]
  next_vertex = labels[(labels.index(vi) + 1) % n]
  
  # Koordynaty dla punktu i dwóch wokół
  vi_coords = generate_dict(coord)[vi]
  prev_coords = generate_dict(coord)[prev_vertex]
  next_coords = generate_dict(coord)[next_vertex]
  
  # Uznajemy, że dla wierzchołka regularnego, środek jest po prawej, gdy
  # poprzedni wierzchołek jest powyżej oraz następnych jest niżej
  interior_right = is_above(prev_coords, vi_coords) and is_below(next_coords, vi_coords)
  
  if interior_right:  # Środek figury na prawo od wierzchołka
    edge_name = f"e{i-1}"
    helper_vertex = helper_dict.get(edge_name)
    
    if helper_vertex and types.get(helper_vertex) == 'merge':
      add_diametral(vi, helper_vertex)
    
    remove_edge(T, edge_name)
    
    insert_edge(T, f"e{i}")
    
    # Set helper(ei) to vi
    helper_dict[f"e{i}"] = vi
    print(f" Pomocnik e{i} = {vi}")
  else:  # Środek figury na lewo od wierzchołka
    edge_left = find_left_edge(T, f"e{i}")
    
    if edge_left:
      helper_vertex = helper_dict.get(edge_left)
      
      if helper_vertex and types.get(helper_vertex) == 'merge':
        add_diametral(vi, helper_vertex)
      
      helper_dict[edge_left] = vi
      print(f" Pomocnik {edge_left} = {vi}")

# Szukamy punktu najbardziej na prawo - o najwyższym "x"
def generate_v_dict(coords):
  dict_of_v = {
  # 'F': 1
  # 'G': 2
 }
  points = generate_dict(coords)
  max_x_key = max(points, key=lambda k: points[k])
  sorted_keys = sorted(points.keys())
  start_index = sorted_keys.index(max_x_key)
  new_order = sorted_keys[start_index:] + sorted_keys[:start_index]
  for i, key in enumerate(new_order):
    dict_of_v[key]= i+1
  return dict_of_v

def generate_e_dict(coords):
  dict_of_e = {
    # 'FG': 1
    # 'GH': 2
  }
  keys = list(generate_v_dict(coords))
  for i in range(len(keys)):
    pair = keys[i] + keys[(i+1) % len(keys)]
    dict_of_e[pair] = i + 1
  return dict_of_e

# MakeMonotone
def make_monotone(coords):
  # Queue: [('J', (7, 15)), ('H', (11, 15)), ('I', (9, 13)), ('K', (5, 12)), ('L', (6, 10)), ('F', (14, 10)), ('N', (4, 9)), ('G', (13, 9)), ('M', (5, 7)), ('D', (7, 5)), ('O', (1, 4)), ('E', (11, 4)), ('B', (6, 2)), ('A', (3, 0)), ('C', (8, -2))]
  queue = priority_queue(coords)
  # Types: {'A': 'end', 'B': 'split', 'C': 'end', 'D': 'split', 'E': 'end', 'F': 'start', 'G': 'merge', 'H': 'start', 'I': 'merge', 'J': 'start', 'K': 'regular', 'L': 'regular', 'M': 'merge', 'N': 'start', 'O': 'regular'}
  types = classify_vertices(coords)
  # Vertices: {'F': 1, 'G': 2, 'H': 3, 'I': 4, 'J': 5, 'K': 6, 'L': 7, 'M': 8, 'N': 9, 'O': 10, 'A': 11, 'B': 12, 'C': 13, 'D': 14, 'E': 15}
  vertices = generate_v_dict(coords)
  # Edges: {'FG': 1, 'GH': 2, 'HI': 3, 'IJ': 4, 'JK': 5, 'KL': 6, 'LM': 7, 'MN': 8, 'NO': 9, 'OA': 10, 'AB': 11, 'BC': 12, 'CD': 13, 'DE': 14, 'EF': 15}
  edges = generate_e_dict(coords)
  
  while queue:
    point = queue[0]
    point_letter = point[0]
    type_of_point = types[point_letter]
    print(f"Stan T: {T}\nWierzchołek: {point}, Typ: {type_of_point}")
    if type_of_point == 'start':
        handle_start_vertex(point, vertices, edges)
    elif type_of_point == 'end':
        handle_end_vertex(point, types, vertices, edges)
    elif type_of_point == 'split':
        handle_split_vertex(point, types, vertices, edges)
    elif type_of_point == 'merge':
        handle_merge_vertex(point, types, vertices, edges)
    else:
        handle_regular_vertex(point, types, vertices, edges)
    print("------------------------")
    queue.pop(0)

def add_diametral(vertice1, vertice2):
  diagonals.append((vertice1, vertice2))
  print(f"  Dodano przekątną pomiędzy {vertice1} a {vertice2}")

if __name__ == "__main__":
  print("\n--- MakeMonotone ---")
  make_monotone(coord)
  print(f"\n--- Diagonals ---\n{diagonals}")
  generate_image()