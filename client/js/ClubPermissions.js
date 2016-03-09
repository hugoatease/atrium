var React = require('react');
var request = require('superagent');
var MemberSearch = require('./MemberSearch');
var PermissionsAdd = require('./PermissionsAdd');

var ClubPermissions = React.createClass({
    getInitialState: function() {
        return {
            permissions: []
        }
    },

    componentDidMount: function() {
        this.fetch();
    },

    fetch: function() {
        request.get('/api/clubs/' + this.props.params.slug + '/permissions')
            .end(function(err, res) {
                if (err) return;
                this.setState({permissions: res.body});
            }.bind(this));
    },

    removePermission: function(permission, profile) {
        request.del('/api/users/' + profile.user.id + '/permissions')
            .send({permission: permission})
            .end(function(err, res) {
                if (err) return;
                this.fetch();
            }.bind(this));
    },

    render: function() {
        return (
            <div className="row">
                <div className="medium-6 column">
                    <h4>Current permissions</h4><hr />
                    {this.state.permissions.map(function(permission) {
                        return (
                            <div className="callout">
                                <h5>{permission._id}</h5>
                                <MemberSearch profiles={permission.profiles} callback={this.removePermission.bind(this, permission._id)} />
                            </div>
                        )
                    }.bind(this))}
                </div>
                <div className="medium-6 column">
                    <h4>Add permissions</h4><hr />
                    <PermissionsAdd club={this.props.params.slug} callback={this.fetch} />
                </div>
            </div>
        );
    }
});

module.exports = ClubPermissions;