/* little hack to show "solution" sections */

$(function() {
    $('.solution').each(function(index, elem) {
        var solution_section = $(elem);
        var show_button = $("<button class='showsoln'>Show</button>");
        var solution_replacement = $('<h3>Solution&nbsp;</h3>');
        solution_replacement.append(show_button);
        solution_section.parent().append(solution_replacement);
        solution_section.hide();
        show_button.click(function() { solution_replacement.hide(); solution_section.show(); });
    });
});
