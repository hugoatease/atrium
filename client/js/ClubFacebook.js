var React = require('react');
var ReactDOM = require('react-dom');
var request = require('superagent');

var ClubFacebook = React.createClass({
    getInitialState: function() {
        return {
            connected: false,
            pages: [],
            current: null
        }
    },

    componentDidMount: function() {
        window.FB.getLoginStatus(function(response) {
            if (response.status === 'connected') {
                this.setState({connected: true});
                this.fetchPages();
            }
        }.bind(this));

        request.get('/api/clubs/' + this.props.params.slug)
            .end(function(err, res) {
                if (err) return;
                this.setState({current: res.body});
            }.bind(this));
    },

    fetchPages: function() {
        window.FB.api('/me/accounts', function(data) {
            this.setState({pages: data.data});
        }.bind(this));
    },

    login: function() {
        window.FB.login(function() {
            this.setState({connected: true});
            this.fetchPages();
        }.bind(this), {scope: 'manage_pages,publish_pages'});
    },

    setPage: function() {
        var page = this.state.pages[ReactDOM.findDOMNode(this.refs.selector).value];
        request.put('/api/clubs/' + this.props.params.slug)
            .send({
               facebook_publish: {
                   id: page.id,
                   name: page.name,
                   access_token: page.name
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
        if (!this.state.connected) {
            return (
                <div className="row">
                    <div className="callout">
                        <h3>Facebook login</h3>
                        <p>
                            You must authorize Atrium with Facebook in order to publish on your pages.
                        </p>
                        <button className="button primary" onClick={this.login}>Login with Facebook</button>
                    </div>
                </div>
            );
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