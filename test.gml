if(state==1)
{
    sprite_index=spr_player_dead;
    gravity=0;
    speed=0;
    if(timer==0){sound_stop_all();sound_play(sound_hit);}
    if(timer==24){sound_play(sound_lose);}
    if(timer==350){game_restart();}
    timer+=1;
    exit;
}
else
{
if(jump==0){
if(keyboard_check(ord('A')))
{
    x-=1;
    image_index-=0.1;
    face=-1;
}
else
if(keyboard_check(ord('D')))
{
    x+=1;
    image_index+=0.15;
    face=1;
}
else
{
    face=0;
}
}

if(keyboard_check_pressed(ord('J')) && jump==0)
{   sound_play(sound_jump);
    direction=90;
    speed=4;
    gravity=0.15;
    jump=1;
    image_index=1;
}
if(jump==1)
{
    x+=face;
}

if(x<16)x=16;
if(x>room_width-16)x=room_width-16;

if(y>206 && direction==270)
{
    y=206;
    speed=0;
    gravity=0;
    jump=0;
    image_index=0;
}
}