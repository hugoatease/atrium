var React = require('react');
var request = require('superagent');
var groupBy = require('lodash/groupBy');
var keys = require('lodash/keys');
var Link = require('react-router').Link;

var Editor = React.createClass({
    getInitialState: function() {
        return {
            permissions: {}
        }
    },

    componentDidMount: function() {
        request.get('/api/profiles/me')
            .end(function(err, res) {
                if (err) return;
                var permissions = groupBy(res.body.user.permissions.map(function(permission) {
                    return {
                        resource: permission.split(':')[1],
                        permission: permission.split(':')[3]
                    }
                }), 'resource');
                this.setState({permissions: permissions});
            }.bind(this));
    },

    render: function() {
        return (
            <div className="row">
                <div className="medium-8 columns">
                    <h4>Your clubs</h4><hr />
                    {keys(this.state.permissions).map(function(club) {
                        var editLink = <Link to={'/editor/clubs/' + club}><button className="button primary">Edit club</button></Link>;
                        var eventsLink = <Link to={'/editor/clubs/' + club + '/events'}><button className="button primary">Events</button></Link>;
                        var newsLink = <Link to={'/editor/clubs/' + club + '/news'}><button className="button primary">News</button></Link>;
                        var permissionsLink = <Link to={'/editor/clubs/' + club + '/permissions'}><button className="button primary">Permissions</button></Link>;
                        var links = {
                            edit: [editLink],
                            events: [eventsLink],
                            news: [newsLink],
                            admin: [editLink, "\u00a0", permissionsLink, "\u00a0", eventsLink, "\u00a0", newsLink]
                        }
                        return (
                            <div className="callout">
                                <h5>{club}</h5>
                                {this.state.permissions[club].map(function(permission) {
                                    return (
                                        <span>{[links[permission.permission], '\u00a0']}</span>
                                    );
                                }.bind(this))}
                            </div>
                        )
                    }.bind(this))}
                </div>
            </div>
        );
    }
});

module.exports = Editor;