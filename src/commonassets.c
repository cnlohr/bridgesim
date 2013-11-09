#include "commonassets.h"


struct UniformMatch * OverallUniforms;
struct Shader * ButtonShader;
struct Shader * TextShader;
struct BitmapFont * OldSansBlack;

float Ambient[4];
float Emission[4];

float TexSlot0;
float TexSlot1;

void SetupCommonAssets()
{
	ButtonShader = CreateShader( "../assets/shaders/button" );
	TextShader = CreateShader( "../assets/shaders/text" );
	OldSansBlack = LoadBitmapFontByName( "../assets/fonts/OldSansBlack.hgfont" );

	OverallUniforms = UniformMatchMake( "AmbientColor", Ambient, 0, 4, 0 );
	OverallUniforms = UniformMatchMake( "EmissionColor", Emission, 0, 4, OverallUniforms );
	OverallUniforms = UniformMatchMake( "tex0", &TexSlot0, 1, 0, OverallUniforms );
	OverallUniforms = UniformMatchMake( "tex1", &TexSlot1, 1, 0, OverallUniforms );
	OverallUniforms = UniformMatchMake( "RenderW", &RenderW, 1, 0, OverallUniforms );
	OverallUniforms = UniformMatchMake( "RenderH", &RenderH, 1, 0, OverallUniforms );

}

void CheckCommonAssets()
{
	CheckForNewerShader( TextShader );
	CheckForNewerShader( ButtonShader );	
}


