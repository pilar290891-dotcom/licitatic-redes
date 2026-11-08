import sys
from PIL import Image
id,out=sys.argv[1],sys.argv[2]
c=Image.new('RGB',(4*360+30, 450+640+10),'white')
for r,(t,h) in enumerate([('ig',1350),('tt',1920)]):
  for i in range(4):
    im=Image.open(f'{out}/{t}_{id}_{i+1}.jpg').resize((360,h//3)); c.paste(im,(i*370, 0 if r==0 else 460))
c.save(f'{out}/sheet_{id}.jpg')
