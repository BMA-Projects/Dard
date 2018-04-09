var toWords = function toWords(n) {
  if (n == 0) return 'zero';
  var a = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen'];
  var b = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety'];
  var g = ['', 'thousand', 'million', 'billion', 'trillion', 'quadrillion', 'quintillion', 'sextillion', 'septillion', 'octillion', 'nonillion'];
  var grp = function grp(n) {
    return ('000' + n).substr(-3);
  };
  var rem = function rem(n) {
    return n.substr(0, n.length - 3);
  };
  var fmt = function fmt(_ref) {
    var h = _ref[0];
    var t = _ref[1];
    var o = _ref[2];

    return [Number(h) === 0 ? '' : a[h] + ' hundred ', Number(o) === 0 ? b[t] : b[t] && b[t] + '-' || '', a[t + o] || a[o]].join('');
  };
  var cons = function cons(xs) {
    return function (x) {
      return function (g) {
        return x ? [x, g && ' ' + g || '', ' ', xs].join('') : xs;
      };
    };
  };
  var iter = function iter(str) {
    return function (i) {
      return function (x) {
        return function (r) {
          if (x === '000' && r.length === 0) return str;
          return iter(cons(str)(fmt(x))(g[i]))(i + 1)(grp(r))(rem(r));
        };
      };
    };
  };
  return iter('')(0)(grp(String(n)))(rem(String(n)));
}
