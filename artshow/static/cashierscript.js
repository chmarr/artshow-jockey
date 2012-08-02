(function() {
  var all_checked;
  $(function() {
    $('.selectables').each(function() {
      var checkboxes, checkboxes_changed, select_all, selectables, tax_node, tax_rate, total_node;
      selectables = $(this);
      select_all = selectables.find('.select_all');
      checkboxes = selectables.find('.item [type=checkbox]');
      select_all.change(function(event) {
        var checked;
        checked = select_all.is(":checked");
        checkboxes.prop('checked', checked);
        return checkboxes_changed();
      });
      checkboxes.change(function(event) {
        var checked, target;
        target = $(event.target);
        checked = target.is(':checked');
        if (!checked) {
          select_all.prop('checked', false);
        }
        if (all_checked(checkboxes)) {
          select_all.prop('checked', true);
        }
        return checkboxes_changed();
      });
      total_node = $('#total');
      tax_node = $('#id_tax-tax_paid');
      totalwithtax_node = $('#totalwithtax');
      tax_rate = 0.0825;
      checkboxes_changed = function() {
        var amount, tax, total, totalwithtax, _i, _len, _ref;
        total = 0;
        _ref = checkboxes.filter(':checked').parents('.item').find('.amount');
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          amount = _ref[_i];
          total += parseInt($(amount).text());
        }
        total_node.text(total);
        tax = (total * tax_rate).toFixed(2);
        totalwithtax = total + parseFloat(tax);
        totalwithtax_node.text ( totalwithtax );
        return tax_node.val(tax);
      };
      return checkboxes_changed();
    });
    return $('.repeatable').each(function() {
      var more_button, repeatable, repeatables, total_forms;
      repeatable = $(this);
      repeatables = repeatable.find('.repeatables');
      more_button = repeatable.find('.more');
      total_forms = $('[name$=TOTAL_FORMS]');
      return more_button.click(function(event) {
        var node, template;
        event.preventDefault();
        template = repeatables.children(':last');
        node = template.clone();
        node.find(':input').val('');
        repeatables.append(node);
        return total_forms.val(parseInt(total_forms.val()) + 1);
      });
    });
  });
  all_checked = function(checkboxes) {
    var checkbox, _i, _len;
    for (_i = 0, _len = checkboxes.length; _i < _len; _i++) {
      checkbox = checkboxes[_i];
      if (!$(checkbox).is(':checked')) {
        return false;
      }
    }
    return true;
  };
}).call(this);
