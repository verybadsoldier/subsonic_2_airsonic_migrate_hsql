# subsonic_2_airsonic_migrate_hsql
Generate SQL statements to migrate ratings and starred files from a Subsonic DB to Airsonic DB

I did this when I migrated from Subsonic to Airsonic Advanced to port my starred media and my ratings to Airsonic. The script will generate SQL INSERT statements that can be executed on the Airsonic DB (e.g. with DBeaver).

Needed input files are JSON dumps of the source Subsonic tables and the destination Airsonic tables. I made those JSON dumps with RazorSQL.
