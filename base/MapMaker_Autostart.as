/*
Script for https://github.com/SonantDread/KAGMapMakerv2
Used to make the 'Test in KAG' button work.
*/
#include "Default/DefaultStart.as"
#include "Default/DefaultLoaders.as"

void Configure()
{
	s_soundon = 1;
	v_driver = 5;
}

void InitializeGame()
{
	print("Initializing Game Script");
	LoadDefaultMapLoaders();
	LoadDefaultMenuMusic();
	RunLocalhost();
	getRules().AddScript("AutoRebuild.as");

	CMap@ map = getMap();
	if (map !is null)
	{
		LoadMap("Maps/MapMaker.png");
	}
}
