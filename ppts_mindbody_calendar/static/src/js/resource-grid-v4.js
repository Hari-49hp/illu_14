/*!
FullCalendar Resource Day Grid Plugin v4.4.2
Docs & License: https://fullcalendar.io/scheduler
(c) 2019 Adam Shaw
*/
! function(e, r) {
    "object" == typeof exports && "undefined" != typeof module ? r(exports, require("@fullcalendar/core"), require("@fullcalendar/resource-common"), require("@fullcalendar/daygrid")) : "function" == typeof define && define.amd ? define(["exports", "@fullcalendar/core", "@fullcalendar/resource-common", "@fullcalendar/daygrid"], r) : r((e = e || self).FullCalendarResourceDayGrid = {}, e.FullCalendar, e.FullCalendarResourceCommon, e.FullCalendarDayGrid)
}(this, (function(e, r, t, o) {
    "use strict";
    var i = "default" in t ? t.default : t,
        n = "default" in o ? o.default : o,
        s = function(e, r) {
            return (s = Object.setPrototypeOf || {
                    __proto__: []
                }
                instanceof Array && function(e, r) {
                    e.__proto__ = r
                } || function(e, r) {
                    for (var t in r) r.hasOwnProperty(t) && (e[t] = r[t])
                })(e, r)
        };

    function a(e, r) {
        function t() {
            this.constructor = e
        }
        s(e, r), e.prototype = null === r ? Object.create(r) : (t.prototype = r.prototype, new t)
    }
    var l = function() {
            return (l = Object.assign || function(e) {
                for (var r, t = 1, o = arguments.length; t < o; t++)
                    for (var i in r = arguments[t]) Object.prototype.hasOwnProperty.call(r, i) && (e[i] = r[i]);
                return e
            }).apply(this, arguments)
        },
        c = function(e) {
            function i(r) {
                var o = e.call(this, r.el) || this;
                return o.splitter = new t.VResourceSplitter, o.slicers = {}, o.joiner = new d, o.dayGrid = r, o
            }
            return a(i, e), i.prototype.firstContext = function(e) {
                e.calendar.registerInteractiveComponent(this, {
                    el: this.dayGrid.el
                })
            }, i.prototype.destroy = function() {
                e.prototype.destroy.call(this), this.context.calendar.unregisterInteractiveComponent(this)
            }, i.prototype.render = function(e, t) {
                var i = this,
                    n = this.dayGrid,
                    s = e.dateProfile,
                    a = e.resourceDayTable,
                    c = e.nextDayThreshold,
                    d = this.splitter.splitProps(e);
                this.slicers = r.mapHash(d, (function(e, r) {
                    return i.slicers[r] || new o.DayGridSlicer
                })), n.receiveContext(t);
                var u = r.mapHash(this.slicers, (function(e, r) {
                    return e.sliceProps(d[r], s, c, t.calendar, n, a.dayTable)
                }));
                n.allowAcrossResources = 1 === a.dayTable.colCnt, n.receiveProps(l({}, this.joiner.joinProps(u, a), {
                    dateProfile: s,
                    cells: a.cells,
                    isRigid: e.isRigid
                }), t)
            }, i.prototype.buildPositionCaches = function() {
                this.dayGrid.buildPositionCaches()
            }, i.prototype.queryHit = function(e, r) {
                var t = this.dayGrid.positionToHit(e, r);
                if (t) return {
                    component: this.dayGrid,
                    dateSpan: {
                        range: t.dateSpan.range,
                        allDay: t.dateSpan.allDay,
                        resourceId: this.props.resourceDayTable.cells[t.row][t.col].resource.id
                    },
                    dayEl: t.dayEl,
                    rect: {
                        left: t.relativeRect.left,
                        right: t.relativeRect.right,
                        top: t.relativeRect.top,
                        bottom: t.relativeRect.bottom
                    },
                    layer: 0
                }
            }, i
        }(r.DateComponent),
        d = function(e) {
            function r() {
                return null !== e && e.apply(this, arguments) || this
            }
            return a(r, e), r.prototype.transformSeg = function(e, r, t) {
                return r.computeColRanges(e.firstCol, e.lastCol, t).map((function(r) {
                    return l({}, e, r, {
                        isStart: e.isStart && r.isStart,
                        isEnd: e.isEnd && r.isEnd
                    })
                }))
            }, r
        }(t.VResourceJoiner),
        u = function(e) {
            function o() {
                var o = null !== e && e.apply(this, arguments) || this;
                return o.flattenResources = r.memoize(t.flattenResources), o.buildResourceDayTable = r.memoize(p), o
            }
            return a(o, e), o.prototype._processOptions = function(t) {
                e.prototype._processOptions.call(this, t), this.resourceOrderSpecs = r.parseFieldSpecs(t.resourceOrder)
            }, o.prototype.render = function(r, t) {
                e.prototype.render.call(this, r, t);
                var o = t.options,
                    i = t.nextDayThreshold,
                    n = this.flattenResources(r.resourceStore, this.resourceOrderSpecs),
                    s = this.buildResourceDayTable(r.dateProfile, r.dateProfileGenerator, n, o.datesAboveResources);
                this.header && this.header.receiveProps({
                    resources: n,
                    dates: s.dayTable.headerDates,
                    dateProfile: r.dateProfile,
                    datesRepDistinctDays: !0,
                    renderIntroHtml: this.renderHeadIntroHtml
                }, t), this.resourceDayGrid.receiveProps({
                    dateProfile: r.dateProfile,
                    resourceDayTable: s,
                    businessHours: r.businessHours,
                    eventStore: r.eventStore,
                    eventUiBases: r.eventUiBases,
                    dateSelection: r.dateSelection,
                    eventSelection: r.eventSelection,
                    eventDrag: r.eventDrag,
                    eventResize: r.eventResize,
                    isRigid: this.hasRigidRows(),
                    nextDayThreshold: i
                }, t)
            }, o.prototype._renderSkeleton = function(r) {
                e.prototype._renderSkeleton.call(this, r), r.options.columnHeader && (this.header = new t.ResourceDayHeader(this.el.querySelector(".fc-head-container"))), this.resourceDayGrid = new c(this.dayGrid)
            }, o.prototype._unrenderSkeleton = function() {
                e.prototype._unrenderSkeleton.call(this), this.header && this.header.destroy(), this.resourceDayGrid.destroy()
            }, o.needsResourceData = !0, o
        }(o.AbstractDayGridView);

    function p(e, r, i, n) {
        var s = o.buildBasicDayTable(e, r);
        return n ? new t.DayResourceTable(s, i) : new t.ResourceDayTable(s, i)
    }
    var y = r.createPlugin({
        deps: [i, n],
        defaultView: "resourceDayGridDay",
        views: {
            resourceDayGrid: u,
            resourceDayGridDay: {
                type: "resourceDayGrid",
                duration: {
                    days: 1
                }
            },
            resourceDayGridWeek: {
                type: "resourceDayGrid",
                duration: {
                    weeks: 1
                }
            },
            resourceDayGridMonth: {
                type: "resourceDayGrid",
                duration: {
                    months: 1
                },
                monthMode: !0,
                fixedWeekCount: !0
            }
        }
    });
    e.ResourceDayGrid = c, e.ResourceDayGridView = u, e.default = y, Object.defineProperty(e, "__esModule", {
        value: !0
    })
}));