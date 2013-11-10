#ifndef _COMMONASSETS_H
#define _COMMONASSETS_H


#include "graphicscore.h"
#include "bitmapfont.h"
#include <os_generic.h>
#include "objreader.h"

extern struct UniformMatch * OverallUniforms;
extern struct Shader * ButtonShader;
extern struct Shader * TextShader;
extern struct BitmapFont * OldSansBlack;

extern float Ambient[4];
extern float Emission[4];

void SetupCommonAssets();
void CheckCommonAssets();

#endif
