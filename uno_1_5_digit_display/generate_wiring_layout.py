"""Verdrahtung in getrennten Ansichten auf dem vorhandenen Platzierungsplan."""
from pathlib import Path
import runpy
from html import escape
from PIL import ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
base = runpy.run_path(str(OUT / 'generate_protoboard_layout.py'))
xy = base['xy']
COLORS = ['#0072b2', '#d55e00', '#009e73', '#a63a98', '#7b6900', '#6254c7', '#008b94', '#bd245d']
# Alle Anschlüsse referenzieren die Draufsicht, nicht die gespiegelte Lötseite.
UNO = {f'D{p}': (1138, 870+(7-p)*40) if p <= 7 else (1138, 610+(13-p)*40) for p in range(2,14)}
UNO.update({f'A{i}': (390,950+i*40) for i in range(6)})
UNO.update({'5V': (390,750), 'GND': (390,790)})
netlist = []
assert UNO['D2'] == (1138,1070) and UNO['D5'] == (1138,950)
assert UNO['D6'] == (1138,910) and UNO['D7'] == (1138,870)
assert UNO['D8'] == (1138,810) and UNO['D13'] == (1138,610)

def page(name, title, rows, foot):
    global img, draw, parts, basename
    basename = name
    img = base['img'].copy(); draw = ImageDraw.Draw(img)
    parts = base['svg'][:-1].copy()
    for box in [(0,0,1600,130),(0,170,275,1205),(1195,170,1600,1205),(0,1250,1600,1450)]:
        draw.rectangle(box,fill='white')
        x,y,x2,y2=box; parts.append(f'<rect x="{x}" y="{y}" width="{x2-x}" height="{y2-y}" fill="white"/>')
    # Außenbeschriftung nach dem Freistellen der Legendenränder erneut zeichnen.
    for arduino_pin, segment in zip(range(2,10), ('a','c','d','e','g','b','f','Zehner')):
        px,py = UNO[f'D{arduino_pin}']
        text(px+72,py-8,segment,16)
    text(70,25,title,30)
    text(70,70,'Bauteilseite / Draufsicht · isolierte Drähte · Kreuzungen sind keine Verbindungen',21)
    text(70,105,'Anschlüsse sind markiert; RN-G = gemeinsamer Anschluss, RN-Ziffer = Widerstandszweig.',18)
    for i,row in enumerate(rows): text(1220,200+i*34,row,18)
    for i,row in enumerate(foot): text(70,1270+i*34,row,19)

def text(x,y,s,size=18,color='#20394d'):
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',size)
    draw.text((x,y),s,font=font,fill=color,anchor='lt')
    parts.append(f'<text x="{x}" y="{y+size*.85}" font-family="Arial" font-size="{size}" fill="{color}">{escape(s)}</text>')

def wire(label, points, color):
    assert len(points)>=2
    # Weißer Rand trennt übereinander laufende isolierte Drähte optisch.
    coords=' '.join(f'{x},{y}' for x,y in points)
    draw.line(points,fill='white',width=8)
    draw.line(points,fill=color,width=4)
    parts.append(f'<polyline points="{coords}" fill="none" stroke="white" stroke-width="8"/>')
    parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="4"/>')
    for x,y in (points[0],points[-1]):
        draw.ellipse((x-5,y-5,x+5,y+5),fill=color,outline='white',width=1)
        parts.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}" stroke="white"/>')
    netlist.append((basename,label))

def save():
    img.save(OUT/f'{basename}.png')
    (OUT/f'{basename}.svg').write_text('\n'.join(parts+['</svg>']),encoding='utf-8')

page('verdrahtung_1_eingaenge','Verdrahtung 1 · Eingänge und RN1',[
'J1: Wert 8 → D10','J2: Wert 4 → D11','J3: Wert 2 → D12','J4: Wert 1 → D13','','RN1-Zweige: 2 / 4 / 6 / 8','je 10 kΩ nach GND','','Kontakte 1/2/3 verbinden','alle führen dasselbe Signal','HIGH = gesetztes Bit'],[
'RN1-G an UNO-GND; Signalquelle benötigt denselben GND (separat, kein eigener GND an J1–J4).',
'RN1-Zweige 1/3/5/7 frei. RN-Pinfolge am realen Bauteil abgleichen.',
'Die drei Kontakte jedes Headers sind verbunden. Unterschiedliche Header bleiben getrennt.'])
for i,col in enumerate((8,10,12,14)):
    p=xy(col,3); q=xy(col,2); color=COLORS[i]
    wire(f'J{i+1}.1 → RN1.{2+2*i}',[p,q],color)
    wire(f'J{i+1}.1 → J{i+1}.2 → J{i+1}.3',[p,xy(col,4),xy(col,5)],color)
    end=UNO[f'D{10+i}']; lane=990+i*25; height=320+i*30
    wire(f'J{i+1}.1 → D{10+i}',[p,(p[0]+16,p[1]),(p[0]+16,height),(lane,height),(lane,end[1]),end],color)
wire('RN1.G → UNO.GND',[xy(6,2),xy(5,2),(550,790),UNO['GND']],'#303030')
wire('J7.1 → J7.2',[xy(3,2),xy(4,2)],'#1976d2')
wire('J7.2 → RN1.G / UNO.GND',[xy(4,2),xy(6,2)],'#1976d2')
gx,gy=xy(5,2)
draw.ellipse((gx-6,gy-6,gx+6,gy+6),fill='#303030')
parts.append(f'<circle cx="{gx}" cy="{gy}" r="6" fill="#303030"/>')
save()

page('verdrahtung_2_leds','Verdrahtung 2 · Arduino → L1–L4 → RN2',[
'A0 → L1.A (Wert 8)','A1 → L2.A (Wert 4)','A2 → L3.A (Wert 2)','A3 → L4.A (Wert 1)','','L1.K → RN2.1','L2.K → RN2.3','L3.K → RN2.5','L4.K → RN2.7','','RN2-G → UNO-GND','je LED: 220 Ω'],[
'Anode oben (Reihe 8), Kathode unten (Reihe 9); RN2 in Reihe 10.',
'RN2-Zweige 2/4/6 bleiben frei. Kein direkter Draht von Eingangssignal zu LED.',
'Arduino schaltet die LEDs; RN2-Pinfolge am Bauteil abgleichen.'])
for i,col in enumerate((8,10,12,14)):
    start=UNO[f'A{i}']; end=xy(col,8); lane=460+i*26
    wire(f'A{i} → L{i+1}.A',[start,(lane,start[1]),(lane,410-i*12),(end[0],410-i*12),end],COLORS[i])
    wire(f'L{i+1}.K → RN2.{1+2*i}',[xy(col,9),xy(col,10)],COLORS[i])
wire('RN2.G → UNO.GND',[xy(7,10),(440,550),(440,790),UNO['GND']],'#303030')
save()

page('verdrahtung_3_uln','Verdrahtung 3 · Arduino → ULN2803A',[
'D2 → U1.1 · a','D3 → U1.2 · c','D4 → U1.3 · d','D5 → U1.4 · e','D6 → U1.5 · g','D7 → U1.6 · b','D8 → U1.7 · f','D9 → U1.8 · Zehner','','U1.9 → UNO-GND','U1.10 (COM): frei'],[
'U1-Kerbe rechts. Eingänge oben: von links nach rechts Pins 9–1.',
'Keine externen Vorwiderstände zwischen UNO und ULN2803A erforderlich.',
'COM (Pin 10) bleibt bei diesen LED-Lasten offen; er ist kein Versorgungspin.'])
for i,arduino_pin in enumerate(range(2,10)):
    start=UNO[f'D{arduino_pin}']; end=xy(14-i,14); lane=990+i*17; y=550-i*14
    wire(f'D{arduino_pin} → U1.{1+i}',[start,(lane,start[1]),(lane,y),(end[0],y),end],COLORS[i])
wire('U1.9 → UNO.GND',[xy(6,14),(480,710),(480,790),UNO['GND']],'#303030')
save()

segments=['Zehner','f','b','g','e','d','c','a']
display_pins=list(range(3,11))
page('verdrahtung_4_anzeige','Verdrahtung 4 · ULN → R1–R8 → Anzeige / +5 V',[
'U1.11 → R1 → Pin 3 (1)','U1.12 → R2 → Pin 4 (f)','U1.13 → R3 → Pin 5 (b)','U1.14 → R4 → Pin 6 (g)','U1.15 → R5 → Pin 7 (e)','U1.16 → R6 → Pin 8 (d)','U1.17 → R7 → Pin 9 (c)','U1.18 → R8 → Pin 10 (a)','','Display-Pins 1/2 → +5 V','R1–R8: je 220 Ω'],[
'Beide Anoden dauerhaft an UNO-5V; kein Multiplexing und keine Anodentransistoren.',
'Strompfad: +5 V → Display-LED → Vorwiderstand → ULN-Ausgang → U1.9 / GND.',
'Gerade Lötbrücken: U1-Pins 11–18 / R1–R8 / Display-Pins 3–10 in denselben Spalten.'])
for i,disp in enumerate(display_pins):
    start=xy(7+i,17); end=xy(7+i,18)
    assert start[0] == end[0]
    wire(f'U1.{11+i} → R{i+1}.1',[start,end],COLORS[i])
    start=xy(7+i,19); end=xy(4+disp,20)
    assert start[0] == end[0]
    wire(f'R{i+1}.2 → Display.{disp}',[start,end],COLORS[i])
start=UNO['5V']
wire('UNO.5V → Display.1',[start,(450,750),(450,930),xy(5,20)],'#df2020')
wire('Display.1 → Display.2',[xy(5,20),xy(6,20)],'#df2020')
save()
page('verdrahtung_5_codierschalter','Verdrahtung 5 · SW1 KMR162 → J1–J4',[
'SW1: Hex-Realcode 0–F',
'C links / rechts → +5 V',
'',
'Bit 1 → J4 → D13',
'Bit 2 → J3 → D12',
'Bit 4 → J2 → D11',
'Bit 8 → J1 → D10',
'',
'Stellung 0: alle Bits LOW',
'Stellung F: alle Bits HIGH',
'RN1 hält offene Bits LOW'],[
'Bauteilseite: Spalte 17 = 1/C/4, Spalte 20 = 8/C/2 (Reihen 1/2/3).',
'Der Sketch zeigt den Eingangswert 0–15; Anzeige und LEDs ändern sich mit den Eingängen.',
'J1–J4 liegen direkt an den Schalterkontakten; keine gleichzeitig treibenden externen Ausgänge anschließen.'])
for bit,col,row,header,target_col,color,lane in [
    (1,17,1,4,14,COLORS[3],970),
    (2,20,3,3,12,COLORS[2],1190),
    (4,17,3,2,10,COLORS[1],990),
    (8,20,1,1,8,COLORS[0],1180),
]:
    start=xy(col,row); end=xy(target_col,5); height=350+header*16
    wire(f'SW1.Bit{bit} → J{header}.3',[start,(lane,start[1]),(lane,height),(end[0],height),end],color)
wire('UNO.5V → SW1.C links',[UNO['5V'],(450,750),(450,145),(1000,145),(1000,230),xy(17,2)],'#df2020')
wire('SW1.C links → SW1.C rechts',[xy(17,2),(1000,230),(1000,340),(1200,340),(1200,230),xy(20,2)],'#df2020')
gx,gy=1000,230
draw.ellipse((gx-6,gy-6,gx+6,gy+6),fill='#df2020')
parts.append(f'<circle cx="{gx}" cy="{gy}" r="6" fill="#df2020"/>')
save()
(OUT/'verdrahtung_verbindungen.txt').write_text('\n'.join(f'{page}: {label}' for page,label in netlist)+'\n',encoding='utf-8')
print(f'5 Verdrahtungsansichten erstellt, {len(netlist)} Drahtverbindungen.')
