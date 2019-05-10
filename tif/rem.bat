ECHO 处于打开状态。
echo Run Tesseract for Training..
tesseract.exe ba.font.exp0.tif ba.font.exp0 nobatch box.train
echo Compute the Character Set..
unicharset_extractor.exe ba.font.exp0.box
mftraining -F font_properties -U unicharset -O ba.unicharset ba.font.exp0.tr
echo Clustering..
cntraining.exe ba.font.exp0.tr
echo Rename Files..
rename normproto ba.normproto
rename inttemp ba.inttemp
rename pffmtable ba.pffmtable
rename shapetable ba.shapetable
echo Create Tessdata.. 
combine_tessdata.exe ba.