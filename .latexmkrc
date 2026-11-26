# latexmk config: build main.tex to PDF with pdflatex
$pdf_mode = 1;
$pdflatex = 'pdflatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
@default_files = ('main.tex');
$clean_ext = 'nav snm vrb synctex.gz';
