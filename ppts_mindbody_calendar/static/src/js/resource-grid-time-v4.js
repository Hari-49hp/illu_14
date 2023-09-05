/*!
FullCalendar Resources Common Plugin v4.4.2
Docs & License: https://fullcalendar.io/scheduler
(c) 2019 Adam Shaw
*/
! function(e, r) {
    "object" == typeof exports && "undefined" != typeof module ? r(exports, require("@fullcalendar/core")) : "function" == typeof define && define.amd ? define(["exports", "@fullcalendar/core"], r) : r((e = e || self).FullCalendarResourceCommon = {}, e.FullCalendar)
}(this, (function(e, r) {
    "use strict";
    var t = function(e, r) {
        return (t = Object.setPrototypeOf || {
                __proto__: []
            }
            instanceof Array && function(e, r) {
                e.__proto__ = r
            } || function(e, r) {
                for (var t in r) r.hasOwnProperty(t) && (e[t] = r[t])
            })(e, r)
    };

    function n(e, r) {
        function n() {
            this.constructor = e
        }
        t(e, r), e.prototype = null === r ? Object.create(r) : (n.prototype = r.prototype, new n)
    }
    var o = function() {
        return (o = Object.assign || function(e) {
            for (var r, t = 1, n = arguments.length; t < n; t++)
                for (var o in r = arguments[t]) Object.prototype.hasOwnProperty.call(r, o) && (e[o] = r[o]);
            return e
        }).apply(this, arguments)
    };

    function s(e, r) {
        var t = e.resourceEditable;
        if (null == t) {
            var n = e.sourceId && r.state.eventSources[e.sourceId];
            n && (t = n.extendedProps.resourceEditable), null == t && null == (t = r.opt("eventResourceEditable")) && (t = r.opt("editable"))
        }
        return t
    }
    var i = function() {
        function e() {
            this.filterResources = r.memoize(u)
        }
        return e.prototype.transform = function(e, r, t, n) {
            if (r.class.needsResourceData) return {
                resourceStore: this.filterResources(t.resourceStore, n.filterResourcesWithEvents, t.eventStore, t.dateProfile.activeRange),
                resourceEntityExpansions: t.resourceEntityExpansions
            }
        }, e
    }();

    function u(e, t, n, s) {
        if (t) {
            var i = function(e, r) {
                var t = {};
                for (var n in e)
                    for (var o = e[n], s = 0, i = r[o.defId].resourceIds; s < i.length; s++) {
                        var u = i[s];
                        t[u] = !0
                    }
                return t
            }(function(e, t) {
                return r.filterHash(e, (function(e) {
                    return r.rangesIntersect(e.range, t)
                }))
            }(n.instances, s), n.defs);
            return o(i, function(e, r) {
                var t = {};
                for (var n in e)
                    for (var o = void 0;
                        (o = r[n]) && (n = o.parentId);) t[n] = !0;
                return t
            }(i, e)), r.filterHash(e, (function(e, r) {
                return i[r]
            }))
        }
        return e
    }
    var a = function() {
        function e() {
            this.buildResourceEventUis = r.memoizeOutput(c, r.isPropsEqual), this.injectResourceEventUis = r.memoize(l)
        }
        return e.prototype.transform = function(e, r, t) {
            if (!r.class.needsResourceData) return {
                eventUiBases: this.injectResourceEventUis(e.eventUiBases, e.eventStore.defs, this.buildResourceEventUis(t.resourceStore))
            }
        }, e
    }();

    function c(e) {
        return r.mapHash(e, (function(e) {
            return e.ui
        }))
    }

    function l(e, t, n) {
        return r.mapHash(e, (function(e, o) {
            return o ? function(e, t, n) {
                for (var o = [], s = 0, i = t.resourceIds; s < i.length; s++) {
                    var u = i[s];
                    n[u] && o.unshift(n[u])
                }
                return o.unshift(e), r.combineEventUis(o)
            }(e, t[o], n) : e
        }))
    }
    var d = {
            id: String
        },
        p = [],
        f = 0;

    function h(e) {
        p.push(e)
    }

    function v(e, t, n) {
        var o = r.refineProps(e, d);
        return o.sourceId = String(f++), o.sourceDefId = n, o.meta = t, o.publicId = o.id, o.isFetching = !1, o.latestFetchId = "", o.fetchRange = null, delete o.id, o
    }

    function g(e, t, n, s) {
        switch (t.type) {
            case "INIT":
                return y(s.opt("resources"), s);
            case "RESET_RESOURCE_SOURCE":
                return y(t.resourceSourceInput, s, !0);
            case "PREV":
            case "NEXT":
            case "SET_DATE":
            case "SET_VIEW_TYPE":
                return function(e, t, n) {
                    return !n.opt("refetchResourcesOnNavigate") || function(e) {
                        return Boolean(p[e.sourceDefId].ignoreRange)
                    }(e) || e.fetchRange && r.rangesEqual(e.fetchRange, t) ? e : E(e, t, n)
                }(e, n.activeRange, s);
            case "RECEIVE_RESOURCES":
            case "RECEIVE_RESOURCE_ERROR":
                return function(e, r, t) {
                    if (r === e.latestFetchId) return o({}, e, {
                        isFetching: !1,
                        fetchRange: t
                    });
                    return e
                }(e, t.fetchId, t.fetchRange);
            case "REFETCH_RESOURCES":
                return E(e, n.activeRange, s);
            default:
                return e
        }
    }
    var R = 0;

    function y(e, r, t) {
        if (e) {
            var n = function(e) {
                for (var r = p.length - 1; r >= 0; r--) {
                    var t = p[r].parseMeta(e);
                    if (t) {
                        var n = v("object" == typeof e && e ? e : {}, t, r);
                        return n._raw = e, n
                    }
                }
                return null
            }(e);
            return !t && r.opt("refetchResourcesOnNavigate") || (n = E(n, null, r)), n
        }
        return null
    }

    function E(e, r, t) {
        var n, s = (n = e.sourceDefId, p[n]),
            i = String(R++);
        return s.fetch({
            resourceSource: e,
            calendar: t,
            range: r
        }, (function(e) {
            t.afterSizingTriggers._resourcesRendered = [null], t.dispatch({
                type: "RECEIVE_RESOURCES",
                fetchId: i,
                fetchRange: r,
                rawResources: e.rawResources
            })
        }), (function(e) {
            t.dispatch({
                type: "RECEIVE_RESOURCE_ERROR",
                fetchId: i,
                fetchRange: r,
                error: e
            })
        })), o({}, e, {
            isFetching: !0,
            latestFetchId: i
        })
    }
    var m = {
            id: String,
            title: String,
            parentId: String,
            businessHours: null,
            children: null,
            extendedProps: null
        },
        S = 0;

    function I(e, t, n, s) {
        void 0 === t && (t = "");
        var i = {},
            u = r.refineProps(e, m, {}, i),
            a = {},
            c = r.processScopedUiProps("event", i, s, a);
        if (u.id || (u.id = "_fc:" + S++), u.parentId || (u.parentId = t), u.businessHours = u.businessHours ? r.parseBusinessHours(u.businessHours, s) : null, u.ui = c, u.extendedProps = o({}, a, u.extendedProps), Object.freeze(c.classNames), Object.freeze(u.extendedProps), n[u.id]);
        else if (n[u.id] = u, u.children) {
            for (var l = 0, d = u.children; l < d.length; l++) {
                I(d[l], u.id, n, s)
            }
            delete u.children
        }
        return u
    }

    function b(e, t, n, s) {
        switch (t.type) {
            case "INIT":
                return {};
            case "RECEIVE_RESOURCES":
                return function(e, r, t, n, o) {
                    if (n.latestFetchId === t) {
                        for (var s = {}, i = 0, u = r; i < u.length; i++) {
                            I(u[i], "", s, o)
                        }
                        return s
                    }
                    return e
                }(e, t.rawResources, t.fetchId, n, s);
            case "ADD_RESOURCE":
                return i = e, u = t.resourceHash, o({}, i, u);
            case "REMOVE_RESOURCE":
                return function(e, r) {
                    var t = o({}, e);
                    for (var n in delete t[r], t) t[n].parentId === r && (t[n] = o({}, t[n], {
                        parentId: ""
                    }));
                    return t
                }(e, t.resourceId);
            case "SET_RESOURCE_PROP":
                return function(e, r, t, n) {
                    var s, i, u = e[r];
                    return u ? o({}, e, ((s = {})[r] = o({}, u, ((i = {})[t] = n, i)), s)) : e
                }(e, t.resourceId, t.propName, t.propValue);
            case "RESET_RESOURCES":
                return r.mapHash(e, (function(e) {
                    return o({}, e)
                }));
            default:
                return e
        }
        var i, u
    }
    var C = {
        resourceId: String,
        resourceIds: function(e) {
            return (e || []).map((function(e) {
                return String(e)
            }))
        },
        resourceEditable: Boolean
    };
    var _ = function() {
        function e(e, r) {
            this._calendar = e, this._resource = r
        }
        return e.prototype.setProp = function(e, r) {
            this._calendar.dispatch({
                type: "SET_RESOURCE_PROP",
                resourceId: this._resource.id,
                propName: e,
                propValue: r
            })
        }, e.prototype.remove = function() {
            this._calendar.dispatch({
                type: "REMOVE_RESOURCE",
                resourceId: this._resource.id
            })
        }, e.prototype.getParent = function() {
            var r = this._calendar,
                t = this._resource.parentId;
            return t ? new e(r, r.state.resourceSource[t]) : null
        }, e.prototype.getChildren = function() {
            var r = this._resource.id,
                t = this._calendar,
                n = t.state.resourceStore,
                o = [];
            for (var s in n) n[s].parentId === r && o.push(new e(t, n[s]));
            return o
        }, e.prototype.getEvents = function() {
            var e = this._resource.id,
                t = this._calendar,
                n = t.state.eventStore,
                o = n.defs,
                s = n.instances,
                i = [];
            for (var u in s) {
                var a = s[u],
                    c = o[a.defId]; - 1 !== c.resourceIds.indexOf(e) && i.push(new r.EventApi(t, c, a))
            }
            return i
        }, Object.defineProperty(e.prototype, "id", {
            get: function() {
                return this._resource.id
            },
            enumerable: !0,
            configurable: !0
        }), Object.defineProperty(e.prototype, "title", {
            get: function() {
                return this._resource.title
            },
            enumerable: !0,
            configurable: !0
        }), Object.defineProperty(e.prototype, "eventConstraint", {
            get: function() {
                return this._resource.ui.constraints[0] || null
            },
            enumerable: !0,
            configurable: !0
        }), Object.defineProperty(e.prototype, "eventOverlap", {
            get: function() {
                return this._resource.ui.overlap
            },
            enumerable: !0,
            configurable: !0
        }), Object.defineProperty(e.prototype, "eventAllow", {
            get: function() {
                return this._resource.ui.allows[0] || null
            },
            enumerable: !0,
            configurable: !0
        }), Object.defineProperty(e.prototype, "eventBackgroundColor", {
            get: function() {
                return this._resource.ui.backgroundColor
            },
            enumerable: !0,
            configurable: !0
        }), Object.defineProperty(e.prototype, "eventBorderColor", {
            get: function() {
                return this._resource.ui.borderColor
            },
            enumerable: !0,
            configurable: !0
        }), Object.defineProperty(e.prototype, "eventTextColor", {
            get: function() {
                return this._resource.ui.textColor
            },
            enumerable: !0,
            configurable: !0
        }), Object.defineProperty(e.prototype, "eventClassNames", {
            get: function() {
                return this._resource.ui.classNames
            },
            enumerable: !0,
            configurable: !0
        }), Object.defineProperty(e.prototype, "extendedProps", {
            get: function() {
                return this._resource.extendedProps
            },
            enumerable: !0,
            configurable: !0
        }), e
    }();
    r.Calendar.prototype.addResource = function(e, r) {
        var t, n, o;
        return void 0 === r && (r = !0), e instanceof _ ? ((t = {})[(o = e._resource).id] = o, n = t) : o = I(e, "", n = {}, this), r && this.component.view.addScroll({
            forcedRowId: o.id
        }), this.dispatch({
            type: "ADD_RESOURCE",
            resourceHash: n
        }), new _(this, o)
    }, r.Calendar.prototype.getResourceById = function(e) {
        if (e = String(e), this.state.resourceStore) {
            var r = this.state.resourceStore[e];
            if (r) return new _(this, r)
        }
        return null
    }, r.Calendar.prototype.getResources = function() {
        var e = this.state.resourceStore,
            r = [];
        if (e)
            for (var t in e) r.push(new _(this, e[t]));
        return r
    }, r.Calendar.prototype.getTopLevelResources = function() {
        var e = this.state.resourceStore,
            r = [];
        if (e)
            for (var t in e) e[t].parentId || r.push(new _(this, e[t]));
        return r
    }, r.Calendar.prototype.rerenderResources = function() {
        this.dispatch({
            type: "RESET_RESOURCES"
        })
    }, r.Calendar.prototype.refetchResources = function() {
        this.dispatch({
            type: "REFETCH_RESOURCES"
        })
    };
    var w = function(e) {
        function r() {
            return null !== e && e.apply(this, arguments) || this
        }
        return n(r, e), r.prototype.getKeyInfo = function(e) {
            return o({
                "": {}
            }, e.resourceStore)
        }, r.prototype.getKeysForDateSpan = function(e) {
            return [e.resourceId || ""]
        }, r.prototype.getKeysForEventDef = function(e) {
            var r = e.resourceIds;
            return r.length ? r : [""]
        }, r
    }(r.Splitter);

    function O(e, r) {
        return o({}, r, {
            constraints: P(e, r.constraints)
        })
    }

    function P(e, r) {
        return r.map((function(r) {
            var t = r.defs;
            if (t)
                for (var n in t) {
                    var o = t[n].resourceIds;
                    if (o.length && -1 === o.indexOf(e)) return !1
                }
            return r
        }))
    }
    r.EventApi.prototype.getResources = function() {
        var e = this._calendar;
        return this._def.resourceIds.map((function(r) {
            return e.getResourceById(r)
        }))
    }, r.EventApi.prototype.setResources = function(e) {
        for (var r = [], t = 0, n = e; t < n.length; t++) {
            var o = n[t],
                s = null;
            "string" == typeof o ? s = o : "number" == typeof o ? s = String(o) : o instanceof _ ? s = o.id : console.warn("unknown resource type: " + o), s && r.push(s)
        }
        this.mutate({
            standardProps: {
                resourceIds: r
            }
        })
    };
    var x = ["GPL-My-Project-Is-Open-Source", "CC-Attribution-NonCommercial-NoDerivatives"],
        T = {
            position: "absolute",
            "z-index": 99999,
            bottom: "1px",
            left: "1px",
            background: "#eee",
            "border-color": "#ddd",
            "border-style": "solid",
            "border-width": "1px 1px 0 0",
            padding: "2px 4px",
            "font-size": "12px",
            "border-top-right-radius": "3px"
        };
    var D = {
        resources: function(e, r, t) {
            var n = r.state.resourceSource._raw;
            t(n, e) || r.dispatch({
                type: "RESET_RESOURCE_SOURCE",
                resourceSourceInput: e
            })
        }
    };

    function j(e, r) {
        return "function" == typeof e ? function(t) {
            return e(new _(r, t))
        } : function(e) {
            return e.title || (0 === (r = e.id).indexOf("_fc:") ? "" : r);
            var r
        }
    }
    h({
        ignoreRange: !0,
        parseMeta: function(e) {
            return Array.isArray(e) ? e : Array.isArray(e.resources) ? e.resources : null
        },
        fetch: function(e, r) {
            r({
                rawResources: e.resourceSource.meta
            })
        }
    }), h({
        parseMeta: function(e) {
            return "function" == typeof e ? e : "function" == typeof e.resources ? e.resources : null
        },
        fetch: function(e, t, n) {
            var o = e.calendar.dateEnv,
                s = e.resourceSource.meta,
                i = {};
            e.range && (i = {
                start: o.toDate(e.range.start),
                end: o.toDate(e.range.end),
                startStr: o.formatIso(e.range.start),
                endStr: o.formatIso(e.range.end),
                timeZone: o.timeZone
            }), r.unpromisify(s.bind(null, i), (function(e) {
                t({
                    rawResources: e
                })
            }), n)
        }
    }), h({
        parseMeta: function(e) {
            if ("string" == typeof e) e = {
                url: e
            };
            else if (!e || "object" != typeof e || !e.url) return null;
            return {
                url: e.url,
                method: (e.method || "GET").toUpperCase(),
                extraParams: e.extraParams
            }
        },
        fetch: function(e, t, n) {
            var s = e.resourceSource.meta,
                i = function(e, r, t) {
                    var n, s, i, u, a = t.dateEnv,
                        c = {};
                    r && (n = t.opt("startParam"), s = t.opt("endParam"), i = t.opt("timeZoneParam"), c[n] = a.formatIso(r.start), c[s] = a.formatIso(r.end), "local" !== a.timeZone && (c[i] = a.timeZone));
                    u = "function" == typeof e.extraParams ? e.extraParams() : e.extraParams || {};
                    return o(c, u), c
                }(s, e.range, e.calendar);
            r.requestJson(s.method, s.url, i, (function(e, r) {
                t({
                    rawResources: e,
                    xhr: r
                })
            }), (function(e, r) {
                n({
                    message: e,
                    xhr: r
                })
            }))
        }
    });
    var F = function(e) {
            function t(t) {
                var n = e.call(this) || this;
                return n.processOptions = r.memoize(n._processOptions), n.parentEl = t, n
            }
            return n(t, e), t.prototype._processOptions = function(e, r) {
                this.datesAboveResources = e.datesAboveResources, this.resourceTextFunc = j(e.resourceText, r)
            }, t.prototype.render = function(e, t) {
                var n, o = t.options,
                    s = t.calendar,
                    i = t.theme;
                this.processOptions(o, s), this.parentEl.innerHTML = "", this.parentEl.appendChild(this.el = r.htmlToElement('<div class="fc-row ' + i.getClass("headerRow") + '"><table class="' + i.getClass("tableGrid") + '"><thead></thead></table></div>')), this.thead = this.el.querySelector("thead"), this.dateFormat = r.createFormatter(o.columnHeaderFormat || r.computeFallbackHeaderFormat(e.datesRepDistinctDays, e.dates.length)), n = 1 === e.dates.length ? this.renderResourceRow(e.resources) : this.datesAboveResources ? this.renderDayAndResourceRows(e.dates, e.resources) : this.renderResourceAndDayRows(e.resources, e.dates), this.thead.innerHTML = n, this.processResourceEls(e.resources)
            }, t.prototype.destroy = function() {
                r.removeElement(this.el)
            }, t.prototype.renderResourceRow = function(e) {
                var r = this,
                    t = e.map((function(e) {
                        return r.renderResourceCell(e, 1)
                    }));
                return this.buildTr(t)
            }, t.prototype.renderDayAndResourceRows = function(e, r) {
                for (var t = [], n = [], o = 0, s = e; o < s.length; o++) {
                    var i = s[o];
                    t.push(this.renderDateCell(i, r.length));
                    for (var u = 0, a = r; u < a.length; u++) {
                        var c = a[u];
                        n.push(this.renderResourceCell(c, 1, i))
                    }
                }
                return this.buildTr(t) + this.buildTr(n)
            }, t.prototype.renderResourceAndDayRows = function(e, r) {
                for (var t = [], n = [], o = 0, s = e; o < s.length; o++) {
                    var i = s[o];
                    t.push(this.renderResourceCell(i, r.length));
                    for (var u = 0, a = r; u < a.length; u++) {
                        var c = a[u];
                        n.push(this.renderDateCell(c, 1, i))
                    }
                }
                return this.buildTr(t) + this.buildTr(n)
            }, t.prototype.renderResourceCell = function(e, t, n) {
                var o = this.context.dateEnv;
                setTimeout(function(){ 
                    document.querySelector("#calendar-event-mindbody > div.fc-view-container > div > table > thead > tr > td > div > table > thead > tr > th.fc-axis.fc-widget-header").innerHTML = "<a class='fc-axis-a' href='/web#id=&action=678&model=availability.availability&view_type=form&cids=1&menu_id=488' style='color:#fff'><i class='fa fa-plus'></i> Add</a>";
                }, 500);

                return '<th class="fc-resource-cell" data-resource-id="' + e.id + '"' + (n ? ' data-date="' + o.formatIso(n, {
                    omitTime: !0
                }) + '"' : "") + (t > 1 ? ' colspan="' + t + '"' : "") + ">  <div class='btn-group'><button type='button' class='btn btn-primary'>" + r.htmlEscape(this.resourceTextFunc(e)) + "</button><button type='button' class='btn btn-primary dropdown-toggle dropdown-toggle-split' data-toggle='dropdown'></button><div class='dropdown-menu'><a class='dropdown-item' href='#'>Go to week view</a><a class='dropdown-item' href='/web#action=665&model=availability.availability&view_type=list&cids=&menu_id=476'>Edit schedule</a><a class='dropdown-item display-none' href='#'>Add unavailability</a><a class='dropdown-item' href='/web#id="+ e.id +"&model=hr.employee&view_type=form&cids=&menu_id=321'>Assign appointment types</a><a class='dropdown-item' href='/web#id="+ e.id +"&model=hr.employee&view_type=form&cids=&menu_id=321'>View profile</a></div></div></th>"
            }, t.prototype.renderDateCell = function(e, t, n) {
                var o = this.props;
                return r.renderDateCell(e, o.dateProfile, o.datesRepDistinctDays, o.dates.length * o.resources.length, this.dateFormat, this.context, t, n ? 'data-resource-id="' + n.id + '"' : "")
            }, t.prototype.buildTr = function(e) {
                return e.length || (e = ["<td>&nbsp;</td>"]), this.props.renderIntroHtml && (e = [this.props.renderIntroHtml()].concat(e)), this.context.isRtl && e.reverse(), "<tr>" + e.join("") + "</tr>"
            }, t.prototype.processResourceEls = function(e) {
                var t = this.context,
                    n = t.calendar,
                    o = t.isRtl,
                    s = t.view;
                r.findElements(this.thead, ".fc-resource-cell").forEach((function(r, t) {
                    t %= e.length, o && (t = e.length - 1 - t);
                    var i = e[t];
                    n.publiclyTrigger("resourceRender", [{
                        resource: new _(n, i),
                        el: r,
                        view: s
                    }])
                }))
            }, t
        }(r.Component),
        U = function() {
            function e(e, r) {
                this.dayTable = e, this.resources = r, this.resourceIndex = new B(r), this.rowCnt = e.rowCnt, this.colCnt = e.colCnt * r.length, this.cells = this.buildCells()
            }
            return e.prototype.buildCells = function() {
                for (var e = this.rowCnt, r = this.dayTable, t = this.resources, n = [], o = 0; o < e; o++) {
                    for (var s = [], i = 0; i < r.colCnt; i++)
                        for (var u = 0; u < t.length; u++) {
                            var a = t[u],
                                c = 'data-resource-id="' + a.id + '"';
                            s[this.computeCol(i, u)] = {
                                date: r.cells[o][i].date,
                                resource: a,
                                htmlAttrs: c
                            }
                        }
                    n.push(s)
                }
                return n
            }, e
        }(),
        A = function(e) {
            function r() {
                return null !== e && e.apply(this, arguments) || this
            }
            return n(r, e), r.prototype.computeCol = function(e, r) {
                return r * this.dayTable.colCnt + e
            }, r.prototype.computeColRanges = function(e, r, t) {
                return [{
                    firstCol: this.computeCol(e, t),
                    lastCol: this.computeCol(r, t),
                    isStart: !0,
                    isEnd: !0
                }]
            }, r
        }(U),
        H = function(e) {
            function r() {
                return null !== e && e.apply(this, arguments) || this
            }
            return n(r, e), r.prototype.computeCol = function(e, r) {
                return e * this.resources.length + r
            }, r.prototype.computeColRanges = function(e, r, t) {
                for (var n = [], o = e; o <= r; o++) {
                    var s = this.computeCol(o, t);
                    n.push({
                        firstCol: s,
                        lastCol: s,
                        isStart: o === e,
                        isEnd: o === r
                    })
                }
                return n
            }, r
        }(U),
        B = function(e) {
            for (var r = {}, t = [], n = 0; n < e.length; n++) {
                var o = e[n].id;
                t.push(o), r[o] = n
            }
            this.ids = t, this.indicesById = r, this.length = e.length
        },
        z = function(e) {
            function t() {
                return null !== e && e.apply(this, arguments) || this
            }
            return n(t, e), t.prototype.getKeyInfo = function(e) {
                var t = e.resourceDayTable,
                    n = r.mapHash(t.resourceIndex.indicesById, (function(e) {
                        return t.resources[e]
                    }));
                return n[""] = {}, n
            }, t.prototype.getKeysForDateSpan = function(e) {
                return [e.resourceId || ""]
            }, t.prototype.getKeysForEventDef = function(e) {
                var r = e.resourceIds;
                return r.length ? r : [""]
            }, t
        }(r.Splitter),
        M = [],
        N = function() {
            function e() {
                this.joinDateSelection = r.memoize(this.joinSegs), this.joinBusinessHours = r.memoize(this.joinSegs), this.joinFgEvents = r.memoize(this.joinSegs), this.joinBgEvents = r.memoize(this.joinSegs), this.joinEventDrags = r.memoize(this.joinInteractions), this.joinEventResizes = r.memoize(this.joinInteractions)
            }
            return e.prototype.joinProps = function(e, r) {
                for (var t = [], n = [], o = [], s = [], i = [], u = [], a = "", c = 0, l = r.resourceIndex.ids.concat([""]); c < l.length; c++) {
                    var d = l[c],
                        p = e[d];
                    t.push(p.dateSelectionSegs), n.push(d ? p.businessHourSegs : M), o.push(d ? p.fgEventSegs : M), s.push(p.bgEventSegs), i.push(p.eventDrag), u.push(p.eventResize), a = a || p.eventSelection
                }
                return {
                    dateSelectionSegs: this.joinDateSelection.apply(this, [r].concat(t)),
                    businessHourSegs: this.joinBusinessHours.apply(this, [r].concat(n)),
                    fgEventSegs: this.joinFgEvents.apply(this, [r].concat(o)),
                    bgEventSegs: this.joinBgEvents.apply(this, [r].concat(s)),
                    eventDrag: this.joinEventDrags.apply(this, [r].concat(i)),
                    eventResize: this.joinEventResizes.apply(this, [r].concat(u)),
                    eventSelection: a
                }
            }, e.prototype.joinSegs = function(e) {
                for (var r = [], t = 1; t < arguments.length; t++) r[t - 1] = arguments[t];
                for (var n = e.resources.length, o = [], s = 0; s < n; s++) {
                    for (var i = 0, u = r[s]; i < u.length; i++) {
                        var a = u[i];
                        o.push.apply(o, this.transformSeg(a, e, s))
                    }
                    for (var c = 0, l = r[n]; c < l.length; c++) {
                        a = l[c];
                        o.push.apply(o, this.transformSeg(a, e, s))
                    }
                }
                return o
            }, e.prototype.expandSegs = function(e, r) {
                for (var t = e.resources.length, n = [], o = 0; o < t; o++)
                    for (var s = 0, i = r; s < i.length; s++) {
                        var u = i[s];
                        n.push.apply(n, this.transformSeg(u, e, o))
                    }
                return n
            }, e.prototype.joinInteractions = function(e) {
                for (var r = [], t = 1; t < arguments.length; t++) r[t - 1] = arguments[t];
                for (var n = e.resources.length, s = {}, i = [], u = !1, a = null, c = 0; c < n; c++) {
                    var l = r[c];
                    if (l) {
                        for (var d = 0, p = l.segs; d < p.length; d++) {
                            var f = p[d];
                            i.push.apply(i, this.transformSeg(f, e, c))
                        }
                        o(s, l.affectedInstances), u = u || l.isEvent, a = a || l.sourceSeg
                    }
                    if (r[n])
                        for (var h = 0, v = r[n].segs; h < v.length; h++) {
                            f = v[h];
                            i.push.apply(i, this.transformSeg(f, e, c))
                        }
                }
                return {
                    affectedInstances: s,
                    segs: i,
                    isEvent: u,
                    sourceSeg: a
                }
            }, e
        }();

    function V(e, r, t, n, o, s) {
        var i = [];
        return function e(r, t, n, o, s, i, u) {
            for (var a = 0; a < r.length; a++) {
                var c = r[a],
                    l = c.group;
                if (l)
                    if (n) {
                        var d = t.length,
                            p = o.length;
                        if (e(c.children, t, n, o.concat(0), s, i, u), d < t.length) {
                            var f = t[d];
                            (f.rowSpans = f.rowSpans.slice())[p] = t.length - d
                        }
                    } else {
                        var h = l.spec.field + ":" + l.value,
                            v = null != i[h] ? i[h] : u;
                        t.push({
                            id: h,
                            group: l,
                            isExpanded: v
                        }), v && e(c.children, t, n, o, s + 1, i, u)
                    }
                else if (c.resource) {
                    h = c.resource.id, v = null != i[h] ? i[h] : u;
                    t.push({
                        id: h,
                        rowSpans: o,
                        depth: s,
                        isExpanded: v,
                        hasChildren: Boolean(c.children.length),
                        resource: c.resource,
                        resourceFields: c.resourceFields
                    }), v && e(c.children, t, n, o, s + 1, i, u)
                }
            }
        }(function(e, r, t, n) {
            var o = function(e, r) {
                    var t = {};
                    for (var n in e) {
                        var o = e[n];
                        t[n] = {
                            resource: o,
                            resourceFields: L(o),
                            children: []
                        }
                    }
                    for (var n in e) {
                        if ((o = e[n]).parentId) {
                            var s = t[o.parentId];
                            s && K(t[n], s.children, r)
                        }
                    }
                    return t
                }(e, n),
                s = [];
            for (var i in o) {
                var u = o[i];
                u.resource.parentId || k(u, s, t, 0, r, n)
            }
            return s
        }(e, n ? -1 : 1, r, t), i, n, [], 0, o, s), i
    }

    function k(e, t, n, o, s, i) {
        n.length && (-1 === s || o <= s) ? k(e, function(e, t, n) {
            var o, s, i = e.resourceFields[n.field];
            if (n.order)
                for (s = 0; s < t.length; s++) {
                    if ((a = t[s]).group) {
                        var u = r.flexibleCompare(i, a.group.value) * n.order;
                        if (0 === u) {
                            o = a;
                            break
                        }
                        if (u < 0) break
                    }
                } else
                    for (s = 0; s < t.length; s++) {
                        var a;
                        if ((a = t[s]).group && i === a.group.value) {
                            o = a;
                            break
                        }
                    }
            o || (o = {
                group: {
                    value: i,
                    spec: n
                },
                children: []
            }, t.splice(s, 0, o));
            return o
        }(e, t, n[0]).children, n.slice(1), o + 1, s, i) : K(e, t, i)
    }

    function K(e, t, n) {
        var o;
        for (o = 0; o < t.length; o++) {
            if (r.compareByFieldSpecs(t[o].resourceFields, e.resourceFields, n) > 0) break
        }
        t.splice(o, 0, e)
    }

    function L(e) {
        var r = o({}, e.extendedProps, e.ui, e);
        return delete r.ui, delete r.extendedProps, r
    }
    var q = r.createPlugin({
        reducers: [function(e, r, t) {
            var n = g(e.resourceSource, r, e.dateProfile, t),
                s = b(e.resourceStore, r, n, t),
                i = function(e, r) {
                    var t;
                    switch (r.type) {
                        case "INIT":
                            return {};
                        case "SET_RESOURCE_ENTITY_EXPANDED":
                            return o({}, e, ((t = {})[r.id] = r.isExpanded, t));
                        default:
                            return e
                    }
                }(e.resourceEntityExpansions, r),
                u = e.loadingLevel + (n && n.isFetching ? 1 : 0);
            return o({}, e, {
                resourceSource: n,
                resourceStore: s,
                resourceEntityExpansions: i,
                loadingLevel: u
            })
        }],
        eventDefParsers: [function(e, t, n) {
            var o = r.refineProps(t, C, {}, n),
                s = o.resourceIds;
            o.resourceId && s.push(o.resourceId), e.resourceIds = s, e.resourceEditable = o.resourceEditable
        }],
        isDraggableTransformers: [function(e, r, t, n) {
            return !(e || !n.viewSpec.class.needsResourceData || !s(r, n.context.calendar)) || e
        }],
        eventDragMutationMassagers: [function(e, r, t) {
            var n = r.dateSpan.resourceId,
                o = t.dateSpan.resourceId;
            n && o && n !== o && (e.resourceMutation = {
                matchResourceId: n,
                setResourceId: o
            })
        }],
        eventDefMutationAppliers: [function(e, r, t) {
            var n = r.resourceMutation;
            if (n && s(e, t)) {
                var o = e.resourceIds.indexOf(n.matchResourceId);
                if (-1 !== o) {
                    var i = e.resourceIds.slice();
                    i.splice(o, 1), -1 === i.indexOf(n.setResourceId) && i.push(n.setResourceId), e.resourceIds = i
                }
            }
        }],
        dateSelectionTransformers: [function(e, r) {
            var t = e.dateSpan.resourceId,
                n = r.dateSpan.resourceId;
            if (t && n) return (!1 !== e.component.allowAcrossResources || t === n) && {
                resourceId: t
            }
        }],
        datePointTransforms: [function(e, r) {
            return e.resourceId ? {
                resource: r.getResourceById(e.resourceId)
            } : {}
        }],
        dateSpanTransforms: [function(e, r) {
            return e.resourceId ? {
                resource: r.getResourceById(e.resourceId)
            } : {}
        }],
        viewPropsTransformers: [i, a],
        isPropsValid: function(e, t) {
            var n = (new w).splitProps(o({}, e, {
                resourceStore: t.state.resourceStore
            }));
            for (var s in n) {
                var i = n[s];
                if (s && n[""] && (i = o({}, i, {
                        eventStore: r.mergeEventStores(n[""].eventStore, i.eventStore),
                        eventUiBases: o({}, n[""].eventUiBases, i.eventUiBases)
                    })), !r.isPropsValid(i, t, {
                        resourceId: s
                    }, O.bind(null, s))) return !1
            }
            return !0
        },
        externalDefTransforms: [function(e) {
            return e.resourceId ? {
                resourceId: e.resourceId
            } : {}
        }],
        eventResizeJoinTransforms: [function(e, r) {
            if (!1 === e.component.allowAcrossResources && e.dateSpan.resourceId !== r.dateSpan.resourceId) return !1
        }],
        // viewContainerModifiers: [function(e, t) {
        //     var n, o = t.opt("schedulerLicenseKey");
        //     n = window.location.href, /\w+\:\/\/fullcalendar\.io\/|\/examples\/[\w-]+\.html$/.test(n) || function(e) {
        //         if (-1 !== x.indexOf(e)) return !0;
        //         var t = (e || "").match(/^(\d+)\-fcs\-(\d+)$/);
        //         if (t && 10 === t[1].length) {
        //             var n = new Date(1e3 * parseInt(t[2], 10)),
        //                 o = new Date(r.config.mockSchedulerReleaseDate || "2020-05-28");
        //             if (r.isValidDate(o))
        //                 if (r.addDays(o, -372) < n) return !0
        //         }
        //         return !1
        //     }(o) || r.appendToElement(e, '<div class="fc-license-message" style="' + r.htmlEscape(r.cssToStr(T)) + '">Please use a valid license key. <a href="http://fullcalendar.io/scheduler/license/">More Info</a></div>')
        // }],
        eventDropTransformers: [function(e, r) {
            var t = e.resourceMutation;
            return t ? {
                oldResource: r.getResourceById(t.matchResourceId),
                newResource: r.getResourceById(t.setResourceId)
            } : {
                oldResource: null,
                newResource: null
            }
        }],
        optionChangeHandlers: D
    });
    e.AbstractResourceDayTable = U, e.DayResourceTable = H, e.ResourceApi = _, e.ResourceDayHeader = F, e.ResourceDayTable = A, e.ResourceSplitter = w, e.VResourceJoiner = N, e.VResourceSplitter = z, e.buildResourceFields = L, e.buildResourceTextFunc = j, e.buildRowNodes = V, e.default = q, e.flattenResources = function(e, r) {
        return V(e, [], r, !1, {}, !0).map((function(e) {
            return e.resource
        }))
    }, e.isGroupsEqual = function(e, r) {
        return e.spec === r.spec && e.value === r.value
    }, Object.defineProperty(e, "__esModule", {
        value: !0
    })
}));