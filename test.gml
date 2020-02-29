var x1,y1,number0,num_len,i,w,index,sgn;
//****函数：显示金钱
x1 = argument0;
y1 = argument1;
number0 = argument2;
num_len = argument3;
sgn = argument4;
//****判断型号
if  num_len == 0 {spr = spr_num6;w = 6;}
if  num_len == 1 {spr = spr_num8_w;w = 8;}
if  num_len == 2 {spr = spr_num8_b;w = 8;}
if  num_len == 3 {spr = spr_num12;w = 12;}
if  num_len == 4 {spr = spr_num18;w = 18;}
if  num_len == 5 {spr = spr_num32;w = 32;}
//****位数
if number0 >99999  num_len = 6;
else
if number0 >9999  num_len = 5;
else
if number0 >999  num_len = 4;
else
if number0 >99  num_len = 3;
else
if number0 >9  num_len = 2;
else num_len = 1;
//****居中
x1 -= num_len*w/2;
//****符号
if sgn == 0 draw_sprite(spr,12,x1,y1);
if sgn == 1 draw_sprite(spr,11,x1,y1);
if sgn == 2 draw_sprite(spr,13,x1,y1);
//****十位-十万位
for(i=0;i<6;i+=1)
{
index = floor(number0/power(10,i)) mod 10;
if number0 > 999999 index = 10;
if number0 < power(10,i) index = 12;
draw_sprite(spr,index,x1+(num_len -i)*w,y1);
}
