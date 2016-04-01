var React = require('react');
var request = require('superagent');
var Link = require('react-router').Link;

var EventList = require('./EventList');
var EventForm = require('./EventForm');

var ClubEvents  = React.createClass({
    render: function() {
        return (
            <div className="row">
                <div className="column medium-6">
                    <div className="clearfix">
                        <h5 className="float-left">Events for {this.props.params.slug}</h5>
                        <Link
                            className="float-right button primary"
                            to={'/editor/clubs/' + this.props.params.slug + '/events/facebook'}>
                            Facebook Import
                        </Link>
                    </div>
                    <EventList club={this.props.params.slug} />
                </div>
                <div className="column medium-6">
                    <h5>Create event</h5><hr />
                    <EventForm club={this.props.params.slug} />
                </div>
            </div>
        );
    }
});

module.exports = ClubEvents;