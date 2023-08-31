setCurrencyField = function (fields, currency) {
    $(function () {
        let groupDiv = '<div class="input-group input-group-narrow"></div>',
            currencySpan = '<span class="input-group-text">' + currency + '</span>';

        for (let i = 0; i < fields.length; i++) {
            $('input[name="' + fields[i] + '"]').wrap(groupDiv).parent('.input-group').append(currencySpan);
        }
    })
}