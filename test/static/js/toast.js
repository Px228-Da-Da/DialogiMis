+function ($) {
  'use strict';

  // TOAST CLASS DEFINITION
  // ======================

  var Toast = function (element, options) {
    this.options             = options
    this.$body               = $(document.body)
    this.$element            = $(element)
    this.$dialog             = this.$element.find('.toast-dialog')
    this.$backdrop           = null
    this.isShown             = null
    this.ignoreBackdropClick = false
  }

  Toast.VERSION  = '1.0.2'

  Toast.TRANSITION_DURATION = 300
  Toast.BACKDROP_TRANSITION_DURATION = 150

  Toast.DEFAULTS = {
    backdrop: true,
    keyboard: true,
    show: true,
    style: 'round',
    timeout: 3000
  }

  Toast.prototype.toggle = function (_relatedTarget) {
    return this.isShown ? this.hide() : this.show(_relatedTarget)
  }

  Toast.prototype.show = function (_relatedTarget) {
    var that = this
    var e    = $.Event('show.bs.toast', { relatedTarget: _relatedTarget })

    this.$element.trigger(e)

    if (this.isShown || e.isDefaultPrevented()) return

    this.isShown = true

    this.$body.addClass('toast-open')

    this.escape()

    this.$element.on('click.dismiss.bs.toast', '[data-dismiss="toast"]', $.proxy(this.hide, this))

    this.$dialog.on('mousedown.dismiss.bs.toast', function () {
      that.$element.one('mouseup.dismiss.bs.toast', function (e) {
        if ($(e.target).is(that.$element)) that.ignoreBackdropClick = true
      })
    })

    this.backdrop(function () {
      var transition = $.support.transition && that.$element.hasClass('fade')

      if (!that.$element.parent().length) {
        that.$element.appendTo(that.$body) // don't move toasts dom position
      }

      that.$element
        .show()
        .scrollTop(0)

      if (transition) {
        that.$element[0].offsetWidth // force reflow
      }

      that.$element.addClass('in')

      switch(that.options.style) {
        case 'round':
          that.$element.addClass('toast-round')
          break
        case 'square':
          that.$element.addClass('toast-square')
          break
        case 'default': // fallthrough
        default:
          that.$element.addClass('toast-default')
          break
      }

      that.enforceFocus()

      var e = $.Event('shown.bs.toast', { relatedTarget: _relatedTarget })

      setTimeout(function () {
        transition ?
          that.$dialog // wait for toast to slide in
            .one('bsTransitionEnd', function () {
              that.$element.trigger('focus').trigger(e)
            })
            .emulateTransitionEnd(Toast.TRANSITION_DURATION) :
          that.$element.trigger('focus').trigger(e),
          that.hide()
        }, that.options.timeout)
    })
  }

  Toast.prototype.hide = function (e) {
    if (e) e.preventDefault()

    e = $.Event('hide.bs.toast')

    this.$element.trigger(e)

    if (!this.isShown || e.isDefaultPrevented()) return

    this.isShown = false

    this.escape()

    $(document).off('focusin.bs.toast')

    this.$element
      .removeClass('in')
      .off('click.dismiss.bs.toast')
      .off('mouseup.dismiss.bs.toast')

    this.$dialog.off('mousedown.dismiss.bs.toast')

    $.support.transition && this.$element.hasClass('fade') ?
      this.$element
        .one('bsTransitionEnd', $.proxy(this.hideToast, this))
        .emulateTransitionEnd(Toast.TRANSITION_DURATION) :
      this.hideToast()
  }

  Toast.prototype.enforceFocus = function () {
    $(document)
      .off('focusin.bs.toast') // guard against infinite focus loop
      .on('focusin.bs.toast', $.proxy(function (e) {
        if (document !== e.target &&
            this.$element[0] !== e.target &&
            !this.$element.has(e.target).length) {
          this.$element.trigger('focus')
        }
      }, this))
  }

  Toast.prototype.escape = function () {
    if (this.isShown && this.options.keyboard) {
      this.$element.on('keydown.dismiss.bs.toast', $.proxy(function (e) {
        e.which == 27 && this.hide()
      }, this))
    } else if (!this.isShown) {
      this.$element.off('keydown.dismiss.bs.toast')
    }
  }

  Toast.prototype.hideToast = function () {
    var that = this
    this.$element.hide()
    this.backdrop(function () {
      that.$body.removeClass('toast-open')
      that.$element.trigger('hidden.bs.toast')
    })
  }

  Toast.prototype.removeBackdrop = function () {
    this.$backdrop && this.$backdrop.remove()
    this.$backdrop = null
  }

  Toast.prototype.backdrop = function (callback) {
    var that = this
    var animate = this.$element.hasClass('fade') ? 'fade' : ''

    if (this.isShown && this.options.backdrop) {
      var doAnimate = $.support.transition && animate

      this.$backdrop = $(document.createElement('div'))
        .addClass('toast-backdrop ' + animate)
        .appendTo(this.$body)

      this.$element.on('click.dismiss.bs.toast', $.proxy(function (e) {
        if (this.ignoreBackdropClick) {
          this.ignoreBackdropClick = false
          return
        }
        if (e.target !== e.currentTarget) return
        this.options.backdrop == 'static'
          ? this.$element[0].focus()
          : this.hide()
      }, this))

      if (doAnimate) this.$backdrop[0].offsetWidth // force reflow

      this.$backdrop.addClass('in')

      if (!callback) return

      doAnimate ?
        this.$backdrop
          .one('bsTransitionEnd', callback)
          .emulateTransitionEnd(Toast.BACKDROP_TRANSITION_DURATION) :
        callback()

    } else if (!this.isShown && this.$backdrop) {
      this.$backdrop.removeClass('in')

      var callbackRemove = function () {
        that.removeBackdrop()
        callback && callback()
      }
      $.support.transition && this.$element.hasClass('fade') ?
        this.$backdrop
          .one('bsTransitionEnd', callbackRemove)
          .emulateTransitionEnd(Toast.BACKDROP_TRANSITION_DURATION) :
        callbackRemove()

    } else if (callback) {
      callback()
    }
  }


  // TOAST PLUGIN DEFINITION
  // =======================

  function Plugin(option, _relatedTarget) {
    return this.each(function () {
      var $this   = $(this)
      var data    = $this.data('bs.toast')
      var options = $.extend({}, Toast.DEFAULTS, $this.data(), typeof option == 'object' && option)

      if (!data) $this.data('bs.toast', (data = new Toast(this, options)))
      if (typeof option == 'string') data[option](_relatedTarget)
      else if (options.show) data.show(_relatedTarget)
    })
  }

  var old = $.fn.toast

  $.fn.toast             = Plugin
  $.fn.toast.Constructor = Toast


  // TOAST NO CONFLICT
  // =================

  $.fn.toast.noConflict = function () {
    $.fn.toast = old
    return this
  }


  // TOAST DATA-API
  // ==============

  $(document).on('click.bs.toast.data-api', '[data-toggle="toast"]', function (e) {
    var $this   = $(this)
    var href    = $this.attr('href')
    var $target = $($this.attr('data-target') || (href && href.replace(/.*(?=#[^\s]+$)/, ''))) // strip for ie7
    var option  = $target.data('bs.toast') ? 'toggle' : $.extend({}, $target.data(), $this.data())

    if ($this.is('a')) e.preventDefault()

    $target.one('show.bs.toast', function (showEvent) {
      if (showEvent.isDefaultPrevented()) return // only register focus restorer if toast will actually get shown
      $target.one('hidden.bs.toast', function () {
        $this.is(':visible') && $this.trigger('focus')
      })
    })
    Plugin.call($target, option, this)
  })

}(jQuery);
