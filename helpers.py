#!/usr/bin/env python
# coding: utf-8

from pocket_cube.constants import CORNERS
from pocket_cube.cube import Cube
from pocket_cube.moves import Move
import numpy as np
from queue import Queue
import random


"""
In acest fisier, helpers.py propunem crearea unor structuri ajutatoare pentru cerint 1
care calculeaza o distanta manhattan pentru fiecare sticker, sau cubulet de tip corner.
Distanta Manhattan pe care o voi calcula este suma tuturor mutarilor minime pentru fiecare
cubulet pentru a ajunge la pozitia si orientarea corecta a culorilor. Pentru 
a fi admisibila, trebuie sa impartim suma la 4, deoarece o miscare
muta 4 cubulete de tip corner.
Am plecat de la distanta Manhattan 3D prezentata la cursul 2, cel
de strategii de cautare. Am folosit-o drept sursa de inspiratie.
Pentru fiecare cubulet de tip corner avem fetele vizibile colorate intr-un anumit mod.

De pilda, pentru cubuletul din pozitia Bottom Bottom-Right
putem avea o configuratie initiala precum
    Față: Alb
    Dreapta: Rosu
    Jos: Verde

Daca aplicam o mutare de tip R, deci dreapta
vom avea următoarele transformări
Față->Sus ; Dreapta->Dreapta; Jos->Față

Cubulețul va avea astfel culorile în următoarea orientare
 Sus: Alb
 Dreapta: Rosu
 Față: Verde      
"""

"""
Mai intai, definim schimbarea fețelor vizibile la aplicarea
fiecărei dintre mutările R,U,F,R',F',U'. Ultimele 3 sunt inverse ale primelor 3.

Pentru o mutare R (dreapta) avem următoarele transformări
dreapta->dreapta
față->sus
sus->spate
spate->jos
jos->față

Pentru U (dreapta)
sus->sus
față->stânga
stânga->spate
spate->dreapta
dreapta->față

Pentru F (față)
față->față
jos->stânga
stânga->sus
sus->dreapta
dreapta->jos

Urmarim conventiile din fisierul constants.py
0-jos
1-sus
2-fata
3-spate
4-stanga
5-dreapta

și adaptăm transformările prin folosirea de dicționare
"""
F_move_for_sides={0:4,4:1,1:5,5:0,2:2}
U_move_for_sides={2:4,4:3,3:5,5:2,1:1}
R_move_for_sides={0:2,2:1,1:3,3:0,5:5}
F_prime_move_for_sides={4:0,1:4,5:1,0:5,2:2}
U_prime_move_for_sides={4:2,3:4,5:3,2:5,1:1}
R_prime_move_for_sides={2:0,1:2,3:1,0:3,5:5}
#introduc apoi dictionarele intr-o lista de dictionare, astfel incat indicii sa se asemene cu cei din clasa Move
moves_for_sides_dictionaries=[R_move_for_sides,F_move_for_sides,U_move_for_sides,R_prime_move_for_sides,F_prime_move_for_sides,
                             U_prime_move_for_sides]


arrangements=[]
while(len(arrangements)<120):
    sample=random.sample([0,1,2,3,4,5],3)
    if(sample not in arrangements):
        arrangements.append(sample)

"""
Urmatoarea functie ia pozitia unui cubulet, pozitie
ce reprezinta cheia din dictionarul CORNERS, o lista de culori
in care culorile sunt asezate exact asa cum indica lista fetelor
vizibile( data fiind o lista sides si o lista color_list
atunci culoare(sides[i])=color_list[i]) si intoarce distanta de la starea in care se afla cubuletul
curent la toate starile posibile la care poate ajunge.
O noua stare este data de schimbarile fetelor vizibile in care
sunt puse culorile, schimbare cauzate de una din cele 6 mutari, un exemplu de schimbare gasindu-se la primul comentariu
din acest fisier sursa.
"""
distances_with_sides_and_colors={}
def compute_possible_distances_and_orientations(start_point,color_list):
    current_dictionary={}
    for position,(_,sides) in CORNERS.items():
        if(position==start_point):
            for i in range(3):
                #asezarea in ordine a culorilor pe fetele vizibile ale cubuletului
                current_dictionary[sides[i]]=color_list[i]
            break
    #pornim cu o cautare BFS de la starea curenta si exploram toate starile posibile din care putem ajunge
    #o stare e data de pozitionarea culorilor pe fetele vizibile ale cubuletului curent
    queue=Queue()
    queue.put((current_dictionary,0))
    parents={}
    initial_state=current_dictionary
    parents[tuple(initial_state.items())]=None
    discovered_states=[]
    while(queue.empty()==False):
        current_state,distance=queue.get()
        discovered_states.append(current_state)
        current_sides=list(current_state.keys())
        distances_with_sides_and_colors[(tuple(initial_state.items()),tuple(current_state.items()))]=distance
        for move_number in range(6):
            considered_dictionary=moves_for_sides_dictionaries[move_number]#mutarea candidat
            missing_side=False
            #luam in considerare doar mutarile in care apar fețele vizibile ale starii vecine
            for side in current_sides:
                if(side not in considered_dictionary):
                    missing_side=True
                    break
            if(missing_side==True):
                continue
            neigh_state={}
            for i in range(3):
                neigh_state[considered_dictionary[current_sides[i]]]=color_list[i]
            if(parents[tuple(current_state.items())] is not None):
                if(parents[tuple(current_state.items())]==tuple(neigh_state.items())):
                    continue
            if(neigh_state in discovered_states):
                continue
            parents[tuple(neigh_state.items())]=current_state
            queue.put((neigh_state,distance+1))
for i in range(2):
    for j in range(2):
        for k in range(2):
            if((i,j,k)!=(0,1,0)):#cubul aflat in pozitia (0,1,0), adica cubul Bottom_TopLeft nu isi schimba pozitia si orientarea
                for color_combo in arrangements:
                    compute_possible_distances_and_orientations((i,j,k),color_combo)

"""
Folosindu-ma de constantele din CORNERS am dorit sa fac maparea intre indicii
fiecarui sticker si culorile corecte sortate in starea finala, respectiv o mapare intre indicii fiecarui sticker
si pozitia sticker-ului.
"""
indices_to_sorted_colors={}
indices_to_positions={}
for position,(indices,_) in CORNERS.items():
    indices_to_sorted_colors[tuple(indices)]=sorted(Cube().goal_state[indices])
    indices_to_positions[tuple(indices)]=position

def minimum_number_of_moves_sticker(given_state:np.ndarray,sticker_indices:list[int],current_sides,end_state:np.ndarray):
    if(sticker_indices==[9,12,16]):#indicii pentru cubuletul Bottom Top Left
        return 0
    correct_colors_order=[]
    #vedem ordinea initiala a culorilor pe care vrem sa o pastram
    for index in sticker_indices:
        correct_colors_order.append(given_state[index])
    colors_sorted=sorted(correct_colors_order)
    result=0
    #folosesc indices_to_positions pentru a obtine pozitia in spatiu actuala a cubuletului
    actual_position=indices_to_positions[tuple(sticker_indices)]
    expected_indices_destination=[]
    #asociem in ordine fiecare fața vizibila cu culoarea corespunzatoare
    initial_state=tuple(zip(current_sides,correct_colors_order))
    #pentru starea finala, pastram culorile asa cum sunt ele in correct_colors_order, 
    #dar vedem care sunt fețele corespunzătoare acestora
    final_state=list(zip([None]*3,correct_colors_order))
    for position,(indices,sides) in CORNERS.items():
        #daca am gasit pentru culorile date indecsii corespunzatori starii finale
        if(indices_to_sorted_colors[tuple(indices)]==colors_sorted):
            for i,index in enumerate(indices):
                color=end_state[index]#pentru culoarea asociata unui index in starea finala
                #in lista starii finale ne asiguram ca pastram ordinea culorilor din correct_colors_order
                #si adaugam fața vizibila pe care se vede culoarea in starea finala
                final_state[correct_colors_order.index(color)]=(sides[i],color)
            final_state=tuple(final_state)
            break
    return distances_with_sides_and_colors[(initial_state,final_state)]

def h1(current_state,end_state):
    result=0
    misplaced_cubies=0
    for initial_position,(indices,current_sides) in CORNERS.items():
        result+=minimum_number_of_moves_sticker(current_state,indices,current_sides,end_state)
    return result/4
