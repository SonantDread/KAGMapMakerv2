/*
KAGMapMakerV2 - An unofficial map maker for King Arthur's Gold.
Copyright (C) 2026 SonantDread

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


Script for https://github.com/SonantDread/KAGMapMakerv2
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
	if (map is null) return;

	LoadMap("Maps/MapMaker.png");
}
