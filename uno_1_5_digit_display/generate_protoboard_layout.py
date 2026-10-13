"""Reproduzierbarer Platzierungsentwurf; keine freigegebene Verdrahtung."""
from pathlib import Path
from html import escape
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
W, H = 1600, 1450
img = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(img)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']

def rect(box, fill, stroke='#20394d', width=2):
    d.rectangle(box, fill=fill, outline=stroke, width=width)
    x,y,x2,y2 = box
    svg.append(f'<rect x="{x}" y="{y}" width="{x2-x}" height="{y2-y}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

def text(x,y,value,size=20,center=False,color='#20394d'):
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', size)
    d.text((x,y),value,font=font,fill=color,anchor='mt' if center else 'lt')
    svg.append(f'<text x="{x}" y="{y+size*.85}" font-family="Arial" font-size="{size}" text-anchor="{"middle" if center else "start"}" fill="{color}">{escape(value)}</text>')

def circle(x,y,r,fill,stroke='#20394d'):
    d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=stroke,width=2)
    svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')

def xy(c,r): return 390+(c-1)*40,190+(r-1)*40
occupied = {}
def pin(c,r,label):
    assert (c,r) not in occupied, (c,r,label,occupied.get((c,r)))
    assert 1 <= c <= 20 and 1 <= r <= 25
    occupied[c,r]=label
    x,y=xy(c,r); circle(x,y,10,'#fff6cf'); text(x,y-6,str(label),12,True)

def header(c,r,labels,name):
    x,y=xy(c,r); rect((x-26,y-20,x+40*(len(labels)-1)+26,y+20),'#e4edf9')
    text(x+20*(len(labels)-1),y-44,name,18,True)
    for i,label in enumerate(labels): pin(c+i,r,label)

def resistor(c,r,name):
    x,y=xy(c,r); rect((x-20,y-20,x+20,y+20),'#ffdda6')
    pin(c,r,'1'); pin(c,r+1,'2')
    if name == 'R1': text(x-65,y+10,'R1',17)
    if name == 'R8': text(x+30,y+10,'R8',17)

rect((0,0,W,H),'white','white')
text(80,25,'UNO-Protoboard · Probebestückung',32)
text(80,70,'Keyestudio aus dem Projektfoto · Draufsicht · UNO unter der Platine',23)
text(80,108,'ENTWURF: Lochbild aus Foto; Anoden direkt +5 V; Verdrahtung noch ausarbeiten.',21,color='#b15b00')
rect((370,170,1170,1210),'#edf1e8','#63735f')
# 20 Spalten / 25 Reihen im Foto. Seitliche Flächen sind für UNO-Leisten reserviert.
for c in range(1,21):
    x,_=xy(c,1); text(x,132 if c >= 17 else 150,str(c),14,True)
for r in range(1,26):
    _,y=xy(1,r); text(285,y-8,str(r),14,True)
    for c in range(1,21):
        if r >= 7 and c in (1,2,18,19,20): continue
        if r >= 11 and c == 3: continue
        if r == 6 and c in (1,20): continue
        x,y=xy(c,r); circle(x,y,9,'#e7c989','#e7c989'); circle(x,y,3,'white','white')
for c,r in [(1,6),(20,6),(3,25),(14,25)]:
    x,y=xy(c,r); circle(x,y+(40 if r == 25 else 0),17,'white','#82947e')
# Anschlussleisten liegen teilweise versetzt zum freien Raster: Foto als Referenz.
def uno_strip(x,ys,labels,title,left=False):
    rect((x-17,min(ys)-20,x+17,max(ys)+20),'#dae4ef')
    for y,label in zip(ys,labels):
        circle(x,y,8,'#fff6cf')
        text(x-65 if left else x+28,y-8,label,16,left)
        if not left and label in {'D2','D3','D4','D5','D6','D7','D8','D9'}:
            segment = {'D2':'a','D3':'c','D4':'d','D5':'e','D6':'g','D7':'b','D8':'f','D9':'Zehner'}[label]
            text(x+72,y-8,segment,16)
    text(x-160 if left else x,min(ys)-49,title,17,True)
uno_strip(1138,[450+i*40 for i in range(10)],['SCL','SDA','AREF','GND','D13','D12','D11','D10','D9','D8'],'DIGITAL')
uno_strip(1138,[870+i*40 for i in range(8)],['D7','D6','D5','D4','D3','D2','D1','D0'],'')
uno_strip(390,[590+i*40 for i in range(8)],['NC','IOREF','RESET','3V3','5V','GND','GND','VIN'],'POWER',True)
uno_strip(390,[950+i*40 for i in range(6)],['A0','A1','A2','A3','A4','A5'],'ANALOG',True)
# SW1: OTAX KMR162, Hex-Realcode 0–F. Draufsicht (Unterseite gespiegelt).
# Sechs Anschlüsse: Spalten 17/20, Reihen 1–3; Abstand 7,62 × 2,54 mm.
x,y=xy(17,1); x2,y2=xy(20,3)
rect((x-19,y-39,x2+19,y2+39),'#252525')
text((x+x2)/2,y-32,'SW1',14,True,color='white')
circle((x+x2)/2,(y+y2)/2,39,'#d32f2f')
text((x+x2)/2,(y+y2)/2-8,'0–F',18,True,color='white')
text((x+x2)/2,y2+19,'KMR162',13,True,color='white')
for row,left,right in [(1,'1','8'),(2,'C','C'),(3,'4','2')]:
    pin(17,row,left); pin(20,row,right)
# Eingangsblock um 90° gedreht: vier senkrechte 3-polige Header
# nebeneinander; jeweils eine freie Spalte zwischen den Headern.
for bit, col in enumerate((8,10,12,14)):
    x,y=xy(col,3)
    rect((x-20,y-20,x+20,y+100),('#252525','#43a047','#fdd835','#ffffff')[bit])
    text(x+24,y+24,f'J{bit+1}',14)
    text(x+24,y+43,str((8,4,2,1)[bit]),14)
    for i in range(3): pin(col,3+i,str(i+1))
# J7: gemeinsamer GND für externe Signalgeber, blau, Reihe 2.
x,y=xy(3,2)
rect((x-20,y-20,x+60,y+20),'#1976d2')
text(x+20,y-45,'J7 · GND',18,True)
pin(3,2,'1'); pin(4,2,'2')
# RN1: Reihe 2, Spalten 6–14.
x,y=xy(6,2); x2,_=xy(14,2)
rect((x-20,y-20,x2+20,y+20),'#ffdda6')
text((x+x2)/2,y-45,'RN1 · 8 × 10 kΩ + GND',18,True)
for i in range(9): pin(6+i,2,'G' if i == 0 else str(i))
text(80,720,'RN1: 8 × 10 kΩ',20)
text(80,756,'gemeinsamer GND',19)
text(80,792,'Pinout vorläufig',18)
text(80,280,'J1–J4 → D10–D13',20)
text(80,316,'aktiv HIGH',20)
text(80,352,'RN1: Pulldowns',19)
text(80,390,'4 × 3 Kontakte',19)
text(80,426,'Je Header: 1–3 gebrückt',18)
text(80,510,'D9 → Zehner',18)
text(80,528,'Anoden → +5 V',20)
text(80,600,'Segmente a–g:',20)
text(80,638,'D2–D8 → U1',20)
text(80,676,'U1 → R2–R8',20)
# LED-Anschlussachsen senkrecht; RN2 waagerecht darunter.
for bit, col in enumerate((8,10,12,14)):
    x,y=xy(col,8); _,y2=xy(col,9)
    rect((x-20,y-17,x+20,y2+17),'#fff0c4')
    circle(x,(y+y2)/2,17,'#ffd35a')
    text(x-45,(y+y2)/2-8,f'L{bit+1}',16)
    pin(col,8,'A'); pin(col,9,'K')
x,y=xy(7,10); x2,_=xy(14,10)
rect((x-20,y-20,x2+20,y+20),'#ffdda6')
text(x2+30,y-8,'RN2',18)
for i in range(8): pin(7+i,10,'G' if i == 0 else str(i))
text(1240,860,'LED1–LED4',20)
text(1240,896,'Arduino A0–A3',18)
text(1240,932,'RN2: 7 × 220 Ω',18)
text(1240,968,'gemeinsamer GND',18)
text(1240,1004,'Zweige 1 / 3 / 5 / 7',18)
# U1: ULN2803A DIP-18, 2,54-mm-Pinraster / 7,62-mm-Reihenabstand.
# Kerbe rechts, Pin 1 oben rechts; Eingänge oben, Ausgänge unten.
x,y=xy(6,14); x2,y2=xy(14,17)
rect((x-18,y-20,x2+18,y2+20),'#e4edf9')
text((x+x2)/2,y+42,'U1 · ULN2803A',23,True)
text(1220,1060,'U1: DIP-18 · Kerbe rechts',16)
d.arc((x2-4,y+40,x2+30,y+80),90,270,fill='#20394d',width=3)
svg.append(f'<path d="M {x2+18} {y+40} A 20 20 0 0 0 {x2+18} {y+80}" fill="none" stroke="#20394d" stroke-width="3"/>')
for i in range(9):
    pin(6+i,14,str(9-i))
    pin(6+i,17,str(10+i))
    if i >= 2:
        segment = ('f','b','g','e','d','c','a')[i-2]
        px,py = xy(6+i,14)
        text(px,py+16,segment,17,True)
        px,py = xy(6+i,17)
        text(px,py-40,segment,17,True)
text(1220,1100,'R1–R8 · je 220 Ω',18)
for i in range(8): resistor(7+i,18,f'R{i+1}')
# Anschlusszeichnung: A–F = Reihen 20–25, 1–12 = Spalten 4–15.
# Pins in A2–A11; Gehäuse zwischen D und E; äußere Spalten bleiben frei.
x,y=xy(4,20); x2,y2=xy(15,25)
rect((x-20,y-20,x2+20,y2+20),'#f7f4e9','#b15b00')
text((x+x2)/2,1180,'J2 · Anzeige · 12 × 6 Lochplätze',18,True)
for r in range(20,26):
    for c in range(4,16):
        hx,hy=xy(c,r); circle(hx,hy,9,'#e7c989','#e7c989'); circle(hx,hy,3,'white','white')
for i in range(10):
    pin(5+i,20,str(i+1))
    px,py=xy(5+i,20)
    if i >= 3:
        text(px+12,py+15,('f','b','g','e','d','c','a')[i-3],17)
    d.line((px,py+12,px,xy(5+i,23)[1]),fill='#20394d',width=3)
    svg.append(f'<line x1="{px}" y1="{py+12}" x2="{px}" y2="{xy(5+i,23)[1]}" stroke="#20394d" stroke-width="3"/>')
x,y=xy(5,23); x2,y2=xy(14,24)
rect((x-18,y,x2+18,y2),'#e4edf9')
text((x+x2)/2,y+10,'Anzeige steht senkrecht',19,True)
circle(x,y+20,17,'white'); circle(x2,y+20,17,'white')
text(1240,260,'J2 · links → rechts',21)
labels=['Anode Einer · +5 V','Anode Zehner · +5 V','Zehner b+c · U1 / R1','f · U1 / R2','b · U1 / R3','g · U1 / R4','e · U1 / R5','d · U1 / R6','c · U1 / R7','a · U1 / R8']
for i,label in enumerate(labels,1): text(1240,300+(i-1)*36,f'{i}: {label}',18)
text(1240,700,'Pin 3 über R1 / U1',19)
text(1240,736,'8. Treiberkanal',18)
text(1240,772,'Steuerung D9',18)
text(770,1225,'VORDERKANTE / Blick auf Anzeigenfront',24,True)
text(80,1270,'Basis: images/Uno und Protoboard.png · seitliche Leisten entsprechen der Fotoausrichtung.',20)
text(80,1307,'Koordinaten dienen der Platzierung; Maße und versetzte UNO-Leisten vor Aufbau prüfen.',20)
text(80,1344,'Anzeige: Spalten 4–15 / Reihen 20–25; Pins 1–10 in Spalten 5–14 / Reihe 20.',20)
text(80,1381,'12 × 6 Lochplätze laut Anschlussbild; Verdrahtung noch offen.',20)
svg.append('</svg>')
(OUT/'protoboard_bestueckung.svg').write_text('\n'.join(svg),encoding='utf-8')
img.save(OUT/'protoboard_bestueckung.png')
img.save(OUT/'protoboard_bestueckung.jpg',quality=95)
print(f'Erstellt: {OUT}/protoboard_bestueckung.{{svg,png,jpg}} · {len(occupied)} Anschlussplätze ohne Überschneidung')
