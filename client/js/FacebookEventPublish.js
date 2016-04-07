var React = require('react');
var ReactDOM = require('react-dom');
var ogp = require('opengraphjs');
var humane = require('humane-js');
var request = require('superagent');

var FacebookEventPublish = React.createClass({
    getInitialState: function() {
        return {
            ogp_image: null,
            ogp_description: null
        }
    },

    componentDidMount: function() {
        ogp({url: window.location.origin + '/events/' + this.props.params.event_id}, function(err, result) {
            console.log(result);
            if (result.description) {
                this.setState({ogp_description: result.description});
            }
            if (result.image && result.image[0]) {
                this.setState({ogp_image: result.image[0].url});
            }
        }.bind(this));
        console.log(this.props);
    },

    publish: function(ev) {
        ev.preventDefault();
        var message = ReactDOM.findDOMNode(this.refs.message).value;
        request.post('/api/events/' + this.props.params.event_id + '/facebook_publish')
            .send({message: message})
            .end(function(err, res) {
                if (err) {
                    humane.log('Failed to publish event on Facebook');
                }
                else {
                    humane.log('Event published on Facebook');
                }
            });
    },

    render: function() {
        return (
            <div className="row">
                <div className="medium-6 column">
                    <h4>Publish on Facebook</h4>
                    <form onSubmit={this.publish}>
                        <textarea rows="10" placeholder="Enter your post's message" ref="message"/>
                        <div className="callout">
                            <img src={this.state.ogp_image} />
                            <p><small>{window.location.origin + '/events/' + this.props.params.event_id}</small></p>
                            <p>{this.state.ogp_description}</p>
                        </div>
                        <button className="button primary">Publish</button>
                    </form>
                </div>
            </div>
        );
    }
});

module.exports = FacebookEventPublish;