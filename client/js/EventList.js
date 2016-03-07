var React = require('react');
var request = require('superagent');
var browserHistory = require('react-router').browserHistory;
var moment = require('moment');

var EventList = React.createClass({
    getDefaultProps: function() {
        return {
            club: null
        }
    },

    getInitialState: function() {
        return {
            events: []
        }
    },

    componentDidMount: function() {
        var r = request.get('/api/events');
        if (this.props.club) {
            r = r.query({club: this.props.club});
        }
        r.end(function(err, res) {
            if (err) return;
            this.setState({
                events: res.body
            });
        }.bind(this));
    },

    select: function(event) {
        browserHistory.push('/editor/events/' + event.id);
    },

    render: function() {
        return (
            <div>
                {this.state.events.map(function(event) {
                    return (
                        <div className="callout" onClick={this.select.bind(this, event)}>
                            <h5>{event.name}</h5>
                            <h6>{moment(event.start_date).format('LL LT')} - {moment(event.end_date).format('LL LT')}</h6>
                            <p dangerouslySetInnerHTML={{__html: event.description}}></p>
                        </div>
                    )
                }.bind(this))}
            </div>
        );
    }
});

module.exports = EventList;