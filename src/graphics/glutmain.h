#ifndef _GLUTMAIN_H
#define _GLUTMAIN_H

extern int fpscount;

//Only in warp mode.
extern double absoluteMouseMotionX;
extern double absoluteMouseMotionY;
extern double currentMouseX;
extern double currentMouseY;


//This must be done in your main.
int StartGlutMain(int argc, char **argv, const char * title, int initsizeX, int initsizeY);
void DoGlutLoop();


//You can call these
void SetMouseWarpMode( int dowarp );

//You have to implement this:
void UpdateDisplay();
void MouseMotion( double x, double y, int mask );
void MouseClick( double x, double y, int button, int state );
void HandleKeyboard( int c, int down );

#endif
