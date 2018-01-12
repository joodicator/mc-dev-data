Array.forEach = Array.forEach || function () {
    var that = arguments[0];
    var args = Array.prototype.slice.call(arguments, 1);
    return Array.prototype.forEach.apply(that, args);
};

window.addEventListener('load', function () {
     Array.forEach(document.getElementsByClassName(
     'pkt-grid-container'), function (div) {
        var left = div.getElementsByClassName('left-header')[0];
        var top = div.getElementsByClassName('top-header')[0];
        var main = div.getElementsByClassName('contents')[0];
        var legend_min = div.getElementsByClassName('legend-min')[0];
        var legend = div.getElementsByClassName('legend')[0];

        var selectedRowIndex = null;
        var selectedRowElems = null;
        Array.forEach(left.getElementsByTagName(
        'tr'), function (leftRow, index) {
            var mainRow = main.getElementsByTagName('tr')[index];
            function onmouseover (ev) {
                if (selectedRowIndex !== null) return;
                if (ev.relatedTarget &&
                    ev.relatedTarget.parentNode.onmouseout === onmouseout) return;
                mainRow.classList.add('highlight');
                leftRow.classList.add('highlight');
                ev.stopPropagation();
            }
            leftRow.onmouseover = mainRow.onmouseover = onmouseover;
            function onmouseout (ev) {
                if (selectedRowIndex !== null) return;
                if (ev.relatedTarget &&
                    ev.relatedTarget.parentNode.onmouseover === onmouseover) return;
                mainRow.classList.remove('highlight');
                leftRow.classList.remove('highlight');
                ev.stopPropagation();
            }
            leftRow.onmouseout = mainRow.onmouseout = onmouseout;
            function onclick (ev) {
                if (selectedRowIndex == index) {
                    selectedRowIndex = selectedRowElems = null;
                    mainRow.classList.remove('highlight');
                    leftRow.classList.remove('highlight');
                } else {
                    selectedRowIndex = index;
                    if (selectedRowElems) selectedRowElems.forEach(function (el) {
                        el.classList.remove('highlight');
                    });
                    mainRow.classList.add('highlight');
                    leftRow.classList.add('highlight');
                    selectedRowElems = [leftRow, mainRow];
                }
                ev.stopPropagation();
            }
            leftRow.onclick = mainRow.onclick = onclick;
        });

        var selectedColIndex = null;
        var selectedColElems = null;
        Array.forEach(top.getElementsByTagName('col'), function (_, index) {
            if (index == 0) return;
            var cells = [];

            function onmouseover (ev) {
                if (selectedColIndex !== null) return;
                if (ev.relatedTarget && (ev.relatedTarget.onmouseout === onmouseout
                    || ev.relatedTarget.parentNode.onmouseout == onmouseout)) return;
                cells.forEach(function (cell) {
                    cell.classList.add('highlight');
                })
            }
            function onmouseout (ev) {
                if (selectedColIndex !== null) return;
                if (ev.relatedTarget && (ev.relatedTarget.onmouseover === onmouseover
                    || ev.relatedTarget.parentNode.onmouseover == onmouseover)) return;
                cells.forEach(function (cell) {
                    cell.classList.remove('highlight');
                });
            }

            function onclick (ev) {
                if (ev.target !== ev.currentTarget) return;
                if (selectedColIndex == index) {
                    selectedColIndex = selectedColElems = null;
                    cells.forEach(function (cell) {
                        cell.classList.remove('highlight');
                    });
                } else {
                    selectedColIndex = index;
                    if (selectedColElems) selectedColElems.forEach(function (el) {
                        el.classList.remove('highlight');
                    });
                    cells.forEach(function (cell) {
                        cell.classList.add('highlight');
                    })
                    selectedColElems = cells;
                }
            }
            Array.forEach(top.getElementsByTagName('tr'), function(tr) {
                var cell = tr.children[index];
                cell.onmouseover = onmouseover;
                cell.onmouseout = onmouseout;
                cell.onclick = onclick;
                cells.push(cell);
            });
            Array.forEach(main.getElementsByTagName('tr'), function (tr) {
                var cell = tr.children[index];
                cells.push(cell);
            });
        });

        legend.classList.add('l-hidden');
        legend_min.onmouseenter = legend_min.onclick = function () {
            legend.classList.replace('l-hidden', 'l-visible');
        };
        legend.onclick = legend.onmouseleave = function () {
            legend.classList.replace('l-visible', 'l-hidden');
            legend_min.onmouseenter = null;
            window.setTimeout(function () {
                legend_min.onmouseenter = legend_min.onclick;
            }, 100);
        };
        Array.forEach(legend.getElementsByTagName('a'), function (a) {
            a.onclick = function (ev) {
                ev.stopPropagation();
            };
        });
    });
});
