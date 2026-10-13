"""Native KiCad schematic with embedded, editable project symbols."""
from pathlib import Path
import uuid, json, re
ROOT=Path(__file__).resolve().parent
NAME='UNO_Anzeige_Zaehler'
UUID=str(uuid.uuid4())
def uid(): return str(uuid.uuid4())
def snap(v): return round(round(v/1.27)*1.27,4)
def quote(s): return json.dumps(s,ensure_ascii=False)
eff='(effects (font (size 1.27 1.27)))'
libs={}; pinmaps={}; nodes={}; expected={}

def poly(points,width=.254):
 return '(polyline (pts '+ ' '.join(f'(xy {x} {y})' for x,y in points)+f') (stroke (width {width}) (type default)) (fill (type none)))'
def rectangle(x1,y1,x2,y2):
 return f'(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.254) (type default)) (fill (type background)))'
def symbol(name,pins,box,graphics=''):
 # Pin coordinates use KiCad symbol convention: local +Y points upward.
 pins=[(str(n),snap(x),snap(y),ang,kind,label) for n,x,y,ang,kind,label in pins]
 pinmaps[name]=pins
 w,t,b=box
 items=[f'(symbol "{name}" (pin_names (offset 1.0)) (in_bom yes) (on_board yes)',
 f'(property "Reference" "U" (at 0 {t+5} 0) {eff})',f'(property "Value" "{name}" (at 0 {t+2.5} 0) {eff})',
 f'(symbol "{name}_0_1" '+rectangle(-w,t,w,b)+graphics+')',f'(symbol "{name}_1_1"']
 for n,x,y,ang,kind,label in pins:
  items.append(f'(pin {kind} line (at {x} {y} {ang}) (length 5.08) (name {quote(label)} {eff}) (number {quote(n)} {eff}))')
 libs[name]='\n'.join(items+['))'])

symbol('UNO_R3',[
 *[(f'D{10+i}',-30,30-5*i,0,'input',f'D{10+i} / IN{8>>i}') for i in range(4)],
 ('A5',-30,10,0,'input','A5 frei'),
 *[(f'A{i}',-30,-10-5*i,0,'output',f'A{i} / L{i+1}') for i in range(4)],
 *[(f'D{9-i}',30,30-5*i,180,'output',f'D{9-i} / '+['T','f','b','g','e','d','c','a'][i]) for i in range(8)],
 ('5V',-5,-50,90,'power_out','+5V'),('GND',5,-50,90,'power_out','GND'),
 ('A4',-30,-35,0,'input','A4 frei')],(25,35,-45))
ulnpins=[]
for i in range(8):
 ulnpins += [(8-i,-20,30-5*i,0,'input',f'IN{8-i}'),(11+i,20,30-5*i,180,'open_collector',f'OUT{8-i}')]
ulnpins += [(9,0,-20,90,'power_in','GND'),(10,0,45,270,'passive','COM')]
symbol('ULN2803A',ulnpins,(15,35,-15))
symbol('Display_1_5_CA',[(3+i,-20,30-5*i,0,'passive',label) for i,label in enumerate(['T / b+c','f','b','g','e','d','c','a'])]+[(1,-20,-20,0,'passive','Anode Einer'),(2,-20,-25,0,'passive','Anode Zehner')],(15,35,-30))
for count,name,value in [(8,'RN_8x10k','10k'),(7,'RN_7x220','220R')]:
 pins=[('G',0,-30,90,'passive','GND gemeinsam')]
 graphics=''
 for i in range(count):
  y=25-i*5
  pins.append((i+1,20,y,180,'passive',f'R{i+1}'))
  graphics+=poly([(0,y),(4,y)])+rectangle(4,y+1,10,y-1)+poly([(10,y),(15,y)])
 graphics+=poly([(0,25),(0,-25)])
 symbol(name,pins,(15,30,-25),graphics)
symbol('Header3',[(i+1,10,2.54-i*2.54,180,'passive',f'{i+1}') for i in range(3)],(5,5.08,-5.08))
symbol('Header2',[(1,10,1.27,180,'passive','Signal'),(2,10,-1.27,180,'passive','GND')],(5,3.81,-3.81))
# Kontaktblock des Hex-Realcode-Schalters; Pinnamen folgen der Funktion.
symbol('KMR162',[
 ('C1',-20,10,0,'passive','Common links'),
 ('C2',-20,-10,0,'passive','Common rechts'),
 *[(str(bit),20,15-10*i,180,'passive',f'Bit {bit}') for i,bit in enumerate([8,4,2,1])]
],(15,20,-20))
# IEC resistor, horizontal.
pinmaps['R_H']=[('1',-7.62,0,0,'passive','~'),('2',7.62,0,180,'passive','~')]
libs['R_H']=f'''(symbol "R_H" (pin_names hide) (pin_numbers hide) (in_bom yes) (on_board yes)
(property "Reference" "R" (at 0 3 0) {eff}) (property "Value" "220R" (at 0 -3 0) {eff})
(symbol "R_H_0_1" {rectangle(-2.5,1,2.5,-1)})
(symbol "R_H_1_1" (pin passive line (at -7.62 0 0) (length 5.08) (name "~" {eff}) (number "1" {eff}))
(pin passive line (at 7.62 0 180) (length 5.08) (name "~" {eff}) (number "2" {eff}))))'''
# Standard KiCad LED graphic, cathode left and anode right.
s=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym').read_text();a=s.index('(symbol "LED"');depth=0;quoted=False
for i in range(a,len(s)):
 c=s[i]
 if c=='"': quoted=not quoted
 if not quoted:
  depth+=(c=='(')-(c==')')
  if depth==0:
   libs['LED']=s[a:i+1];break
pinmaps['LED']=[('1',-3.81,0,0,'passive','K'),('2',3.81,0,180,'passive','A')]
# Use one local library, also embed definitions for portable opening.
(ROOT/'UNO_Project.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor") '+'\n'.join(libs.values())+')')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "UNO_Project") (type "KiCad") (uri "${KIPRJMOD}/UNO_Project.kicad_sym") (options "") (descr "UNO-Binaeranzeige")))')
out=[f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {UUID}) (paper "A3") (title_block (title "UNO: 1 1/2-stellige Binaeranzeige") (rev "1.0") (comment 1 "J1-J4 / SW1: Binaereingaenge 0-15"))',
 '(lib_symbols '+'\n'.join(v.replace(f'(symbol "{n}"',f'(symbol "UNO_Project:{n}"',1) for n,v in libs.items())+')']
def text(x,y,s,size=1.6): out.append(f'(text {quote(s)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left)) (uuid {uid()}))')
def wire(p,q):
 p=tuple(map(snap,p));q=tuple(map(snap,q))
 if p==q:return
 out.append(f'(wire (pts (xy {p[0]} {p[1]}) (xy {q[0]} {q[1]})) (stroke (width 0) (type default)) (uuid {uid()}))')
def junction(p):
 p=tuple(map(snap,p));out.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid {uid()}))')
def label(p,net):
 p=tuple(map(snap,p));out.append(f'(label {quote(net)} (at {p[0]} {p[1]} 0) (effects (font (size 1.1 1.1)) (justify left bottom)) (uuid {uid()}))')
def nc(p):out.append(f'(no_connect (at {p[0]} {p[1]}) (uuid {uid()}))')
def place(name,ref,value,x,y,nets,offset=None):
 x,y=snap(x),snap(y)
 ident=uid();out.append(f'(symbol (lib_id "UNO_Project:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {ident})')
 if offset is None:offset=(-40,-37.5) if name=='UNO_R3' else (-40,-37.5) if name in ['ULN2803A','Display_1_5_CA'] else (-38,-35.5) if name.startswith('RN_') else (-8,-5.5)
 for prop,val,dy in [('Reference',ref,offset[0]),('Value',value,offset[1])]:
  prop_x=x+(-5 if prop=='Reference' else 5) if name=='R_H' else x
  prop_y=y-2 if name=='R_H' else y+dy
  out.append(f'(property "{prop}" {quote(val)} (at {prop_x} {prop_y} 0) {eff})')
 for num,*_ in pinmaps[name]:out.append(f'(pin {quote(num)} (uuid {uid()}))')
 out.append(f'(instances (project "{NAME}" (path "/{UUID}" (reference "{ref}") (unit 1)))) )')
 for num,px,py,ang,kind,pname in pinmaps[name]:
  p=(round(x+px,4),round(y-py,4));nodes[ref,num]=p;expected[ref,num]=nets[num]
  if nets[num] is None:nc(p)
 return ident

def stub(ref,pin,net,direction='right',length=10):
 p=nodes[ref,str(pin)];q=(p[0]+length if direction=='right' else p[0]-length,p[1]);wire(p,q);label(q,net)

text(20,18,'UNO-Protoboard: Binaeranzeige 0-15',3)
text(20,26,'D2-D9: ULN-Kanaele 1-8 | D10-D13: Eingangsbits 8-4-2-1 | A0-A3: Status-LEDs | A4/A5: frei',1.7)
text(20,37,'Eingaenge: aktive 0/5-V-Signale',2)
for i,value in enumerate([8,4,2,1]):
 ref=f'J{i+1}';net=f'IN{value}';place('Header3',ref,f'Bit {value}',30,55+i*20,{str(p):net for p in range(1,4)})
 points=[nodes[ref,str(p)] for p in range(1,4)];trunk=points[0][0]+5
 for p in points:wire(p,(trunk,p[1]))
 wire((trunk,points[0][1]),(trunk,points[-1][1]));junction((trunk,points[1][1]));label((trunk,points[1][1]),net)
place('Header2','J7','GND extern / blau',92,172,{'1':'GND','2':'GND'})
stub('J7',1,'GND');stub('J7',2,'GND')
rn1={str(i):None for i in range(1,9)};rn1.update({'G':'GND','2':'IN8','4':'IN4','6':'IN2','8':'IN1'})
place('RN_8x10k','RN1','8 x 10k / GND',92,85,rn1)
for pin,net in rn1.items():
 if net:stub('RN1',pin,net)
text(66,130,'RN1: Zweige 1/3/5/7 frei.',1.4)
text(20,160,'J1-J4: je alle drei Kontakte verbunden.',1.4)
uno={f'D{10+i}':f'IN{8>>i}' for i in range(4)};uno.update({f'D{2+i}':f'DRV{i+1}' for i in range(8)});uno.update({f'A{i}':f'LED{i+1}_A' for i in range(4)});uno.update({'A5':None,'5V':'+5V','GND':'GND','A4':None})
place('UNO_R3','A1','Arduino UNO R3',182,85,uno)
for pin,net in uno.items():
 if net and pin not in [f'D{i}' for i in range(2,10)]:stub('A1',pin,net,'left' if pin.startswith('A') or pin.startswith('D') or pin=='5V' else 'right',7.62)
text(153,142,'USB: 5 V / DC-Buchse: 7-9 V',1.5)
text(153,147,'DC-Mittelkontakt Plus.',1.5)
text(153,152,'5V/GND versorgen das Protoboard.',1.5)
uln={str(i):f'DRV{i}' for i in range(1,9)};uln.update({str(11+i):f'SINK{i+1}' for i in range(8)});uln.update({'9':'GND','10':None})
place('ULN2803A','U1','ULN2803A / DIP-18',245,85,uln)
for i in range(1,9):wire(nodes['A1',f'D{i+1}'],nodes['U1',str(i)])
stub('U1',9,'GND')
text(229,35,'COM / Pin 10: frei',1.4)
segments=['T / b+c','f','b','g','e','d','c','a']
disp={str(i+3):f'K{i+3}' for i in range(8)};disp.update({'1':'+5V','2':'+5V'})
place('Display_1_5_CA','DS1','1 1/2-stellig / rot / CA',352,85,disp)
for i in range(8):
 ref=f'R{i+1}';y=nodes['U1',str(11+i)][1]
 place('R_H',ref,'220R',297,y,{'1':f'SINK{i+1}','2':f'K{i+3}'},(-1.8,1.8))
 wire(nodes['U1',str(11+i)],nodes[ref,'1']);wire(nodes[ref,'2'],nodes['DS1',str(3+i)])
# Same net, explicit junction between the two permanently supplied anodes.
p=nodes['DS1','1'];q=nodes['DS1','2'];wire(p,(320,p[1]));wire(q,(320,q[1]));wire((320,p[1]),(320,q[1]));junction((320,p[1]));wire((320,p[1]),(310,p[1]));label((310,p[1]),'+5V')
text(268,134,'U1.11 -> R1 -> DS1.3 (Zehner)',1.4)
text(268,139,'U1.12-18 -> R2-8 -> DS1.4-10',1.4)
text(268,144,'Anoden 1/2 fest an +5V; kein Multiplexing.',1.4)
text(20,184,'Status-LEDs: Arduino-Ausgaenge, getrennt von J1-J4',2)
rn2={str(i):None for i in range(1,8)};rn2['G']='GND'
for i in range(4):rn2[str(1+2*i)]=f'LED{i+1}_K'
place('RN_7x220','RN2','7 x 220R / GND',92,230,rn2)
for i in range(4):
 y=nodes['RN2',str(1+2*i)][1]
 place('LED',f'L{i+1}',f'Bit {8>>i}',148,y,{'1':f'LED{i+1}_K','2':f'LED{i+1}_A'},(-3.5,3))
 wire(nodes['RN2',str(1+2*i)],nodes[f'L{i+1}','1'])
 stub(f'L{i+1}',2,f'LED{i+1}_A')
stub('RN2','G','GND')
text(20,267,'RN-Pinnummern sind Zweigbezeichnungen (G = gemeinsam), keine bestaetigte Gehaeuse-Pinfolge.',1.4)
sw={'C1':'+5V','C2':'+5V',**{str(bit):f'IN{bit}' for bit in [1,2,4,8]}}
place('KMR162','SW1','OTAX KMR162 / 0-F',355,213,sw,(-27,-24))
for pin,net in sw.items():stub('SW1',pin,net,'left' if pin.startswith('C') else 'right',7.62)
text(329,241,'Realcode: 0 = offen, F = alle Bits.',1.3)
text(329,247,'C1/C2: beide an +5V.',1.3)
text(195,195,'Direkte Anzeige der Binaereingaenge',2)
text(195,203,'J1-J4 / SW1: Eingangswert 0-15.',1.5)
text(195,211,'Ab 10: Zehner an; Einer = Wert modulo 10.',1.5)
text(195,219,'Unveraenderte Eingaenge halten die Anzeige.',1.5)
text(195,227,'Start: 0, danach aktuellen Eingangswert lesen.',1.5)
text(195,239,'Alle Signalquellen brauchen gemeinsamen GND.',1.5)
text(195,247,'UNO-Modul ist als Anschlussblock dargestellt.',1.5)
text(195,255,'RN-Pinfolge und Displaymaße am Bauteil abgleichen.',1.5)
out.append(')');(ROOT/f'{NAME}.kicad_sch').write_text('\n'.join(out))
(ROOT/f'{NAME}.kicad_pro').write_text(json.dumps({'meta':{'filename':f'{NAME}.kicad_pro','version':1}},indent=2))
(ROOT/'expected_nets.json').write_text(json.dumps({f'{ref}.{pin}':net for (ref,pin),net in expected.items() if net is not None},indent=2))
print('Generated native KiCad schematic:',ROOT/f'{NAME}.kicad_sch')
