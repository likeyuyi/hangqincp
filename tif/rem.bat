ECHO 处于打开状态。
echo Run Tesseract for Training..
tesseract.exe fs.font.exp0.tif fs.font.exp0 nobatch box.train
echo Compute the Character Set..
unicharset_extractor.exe fs.font.exp0.box
mftraining -F font_properties -U unicharset -O fs.unicharset fs.font.exp0.tr
echo Clustering..
cntraining.exe fs.font.exp0.tr
echo Rename Files..
rename normproto fs.normproto
rename inttemp fs.inttemp
rename pffmtable fs.pffmtable
rename shapetable fs.shapetable
echo Create Tessdata.. 
combine_tessdata.exe fs.