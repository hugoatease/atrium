var React = require('react');
var ReactDOM = require('react-dom');
var request = require('superagent');
var humane = require('humane-js');

var PermissionsEnroll = React.createClass({
    getInitialState: function() {
        return {
            token: null
        }
    },

    enroll: function(ev) {
        ev.preventDefault();
        var permission = ReactDOM.findDOMNode(this.refs.permission).value;

        request.post('/api/permissions/enroll/' + permission)
            .end(function(err, res) {
                if (err) {
                    humane.log('Failed to create token')
                }
                else {
                    humane.log('Created token');
                    this.setState({
                        token: res.body.enroll_url
                    });
                }
            }.bind(this));
    },

    render: function() {
        return (
            <div className="row">
                <div className="small-12">
                    <form onSubmit={this.enroll}>
                        <label>
                            <span>Permission identifier</span>
                            <input type="text" placeholder="Permission identifier" ref="permission" />
                        </label>
                        <label>
                            <span>Token</span>
                            <textarea readOnly={true} value={this.state.token} rows={4}></textarea>
                        </label>
                        <button className="button success" type="submit">Create token</button>
                    </form>
                </div>
            </div>
        )
    }
});

module.exports = PermissionsEnroll;