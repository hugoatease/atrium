var React = require('react');
var ReactDOM = require('react-dom');
var request = require('superagent');
var find = require('lodash/find');

var ClubFacebook = React.createClass({
    getInitialState: function() {
        return {
            connected: false,
            authorized: false,
            pages: [],
            current: null
        }
    },

    componentDidMount: function() {
        if (this.props.user.facebook_token) {
            this.setState({connected: true});
            window.FB.api('/me/permissions', {access_token: this.props.user.facebook_token}, function(response) {
                var manage = find(response.data, {permission: 'manage_pages', status: 'granted'});
                var publish = find(response.data, {permission: 'publish_pages', status: 'granted'});
                if (manage && publish) {
                    this.setState({authorized: true});
                    this.fetchPages();
                }
            }.bind(this));
        }

        request.get('/api/clubs/' + this.props.params.slug)
            .end(function(err, res) {
                if (err) return;
                this.setState({current: res.body});
            }.bind(this));
    },

    fetchPages: function() {
        window.FB.api('/me/accounts', {access_token: this.props.user.facebook_token}, function(data) {
            this.setState({pages: data.data});
        }.bind(this));
    },

    setPage: function() {
        var page = this.state.pages[ReactDOM.findDOMNode(this.refs.selector).value];
        request.put('/api/clubs/' + this.props.params.slug)
            .send({
               facebook_publish: {
                   id: page.id,
                   name: page.name,
                   access_token: page.access_token
               }
            })
            .end(function(err, res) {
                if (err) return;
                this.setState({current: res.body});
            }.bind(this));
    },

    resetPage: function() {
        request.put('/api/clubs/' + this.props.params.slug)
            .send({
               facebook_publish: {id: null}
            })
            .end(function(err, res) {
                if (err) return;
                this.setState({current: res.body});
            }.bind(this));
    },

    render: function() {
        if (!this.state.authorized) {
            if (!this.state.connected) {
                return (
                    <div className="row">
                        <div className="callout">
                            <h3>Facebook login</h3>
                            <p>
                                You must link your Atrium account in Facebook in order to use Facebook integration.
                            </p>
                            <a className="button primary" href="https://www.atrium-app.com/sso">Check your account</a>
                        </div>
                    </div>
                );
            }
            else {
                return (
                    <div className="row">
                        <div className="callout">
                            <h3>Missing Facebook permissions</h3>
                            <p>
                                You must grant Facebook page management permissions in order to publish on pages.
                            </p>
                            <a
                                className="button primary"
                                href={'/login?facebook_additional_permissions=manage_pages,publish_pages&next=' + window.location.pathname}>
                                Grant permissions
                            </a>
                        </div>
                    </div>
                );
            }
        }
        else {
            var current = null;
            if (this.state.current && this.state.current.facebook_publish.id) {
                current = <p><b>Current page: </b>{this.state.current.facebook_publish.name}</p>
            }
            return (
                <div className="row">
                    <div className="callout">
                        <h4>Facebook publishing for {this.props.params.slug}</h4>
                        {current}
                        <select ref="selector">
                            {this.state.pages.map(function(page, index) {
                                return (
                                    <option value={index}>{page.name}</option>
                                );
                            }.bind(this))}
                        </select>
                        <button className="button success" onClick={this.setPage}>Change page</button>
                        <br />
                        <button className="button alert" onClick={this.resetPage}>Reset page</button>
                    </div>
                </div>
            );
        }
    }
});

module.exports = ClubFacebook;