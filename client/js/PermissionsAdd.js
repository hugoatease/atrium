var React = require('react');
var request = require('superagent');
var MemberSearch = require('./MemberSearch');
var toPairs = require('lodash/toPairs');

var PermissionsAdd = React.createClass({
    getDefaultProps: function() {
        return {
            callback: null
        }
    },

    getInitialState: function() {
        return {
            permissions: null,
            selected_permission: null
        }
    },

    componentDidMount: function() {
        request.get('/api/permissions')
            .end(function(err, res) {
                if (err) return;
                this.setState({
                    permissions: res.body,
                    selected_permission: toPairs(res.body.club)[0][0]
                });
            }.bind(this));
    },

    selected: function(profile) {
        request.post('/api/users/' + profile.user.id + '/permissions')
            .send({permission: 'club:' + this.props.club + '::' + this.state.selected_permission})
            .end(function(err, res) {
                if (err) return;
                if (this.props.callback) {
                    this.props.callback({
                        permission: 'club:' + this.props.club + '::' + this.state.selected_permission,
                        profile: profile
                    });
                }
            }.bind(this));
    },

    permissionChange: function(ev) {
        this.setState({selected_permission: ev.target.value});
    },

    render: function() {
        var selector = null;
        if (this.state.permissions) {
            selector = toPairs(this.state.permissions.club).map(function(pair) {
               return (
                    <option value={pair[0]}>{pair[1]}</option>
               );
            });
        }

        return (
            <div>
                <label>
                    Select permission to add
                    <select value={this.state.selected_permission} onChange={this.permissionChange}>
                        {selector}
                    </select>
                </label>
                <MemberSearch callback={this.selected} />
            </div>
        );
    }
});

module.exports = PermissionsAdd;