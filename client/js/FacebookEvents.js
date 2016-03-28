var React = require('react');
var request = require('superagent');
var humane = require('humane-js');
var moment = require('moment');

var FacebookEvents = React.createClass({
    getInitialState: function() {
        return {
            events: []
        }
    },

    componentDidMount: function() {
        this.fetch();
    },

    fetch: function() {
        request.get('/api/clubs/' + this.props.params.slug + '/facebook_events')
            .end(function(err, res) {
               if (err) return;
                this.setState({events: res.body});
            }.bind(this));
    },

    importEvent: function(id) {
        humane.log('Importing ' + id + '. Please wait');
        request.post('/api/events')
            .send({
                club: this.props.params.slug,
                facebook_id: id
            })
            .end(function(err, res) {
                if (err) {
                    humane.log('Failed to import ' + id);
                }
                else {
                    humane.log(id + ' has been imported');
                }
            }.bind(this));
    },

    render: function() {
        return (
            <div>
                <div className="row">
                    <h4>Facebook events</h4>
                    <p>Click on an event below to import it on Atrium</p>
                </div>
                <div className="row medium-up-2">
                    {this.state.events.map(function(event) {
                        return (
                            <div className="column callout" onClick={this.importEvent.bind(this, event.id)}>
                                <h5>{event.name}</h5>
                                <h6>{moment(event.start_time).format('LL LT')} - {moment(event.end_time).format('LL LT')}</h6>
                            </div>
                        );
                    }.bind(this))}
                </div>
            </div>
        );
    }
});

module.exports = FacebookEvents;