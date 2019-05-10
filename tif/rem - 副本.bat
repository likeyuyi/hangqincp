ECHO 处于打开状态。
echo Run Tesseract for Training..
tesseract.exe bh.font.exp0.tif bh.font.exp0 nobatch box.train
echo Compute the Character Set..
unicharset_extractor.exe bh.font.exp0.box
mftraining -F font_properties -U unicharset -O bh.unicharset bh.font.exp0.tr
echo Clustering..
cntraining.exe bh.font.exp0.tr
echo Rename Files..
rename normproto bh.normproto
rename inttemp bh.inttemp
rename pffmtable bh.pffmtable
rename shapetable bh.shapetable
echo Create Tessdata.. 
combine_tessdata.exe bh.