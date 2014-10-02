CSS_TARGETS := index.min.css index.css common/fullwindow_canvas.min.css common/fullwindow_canvas.css

all: $(CSS_TARGETS)

FULLWINDOW_CANVAS_DEPS := common/fullwindow_canvas.gss
common/fullwindow_canvas.css: $(FULLWINDOW_CANVAS_DEPS)
	closure-stylesheets --pretty-print -o $@ $^

common/fullwindow_canvas.min.css: $(FULLWINDOW_CANVAS_DEPS)
	closure-stylesheets -o $@ $^

INDEX_DEPS := index.gss common/fullwindow_canvas.gss
index.css: $(INDEX_DEPS)
	closure-stylesheets --pretty-print -o $@ $^

index.min.css: $(INDEX_DEPS)
	closure-stylesheets -o $@ $^
