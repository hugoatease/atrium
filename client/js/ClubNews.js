var React = require('react');
var request = require('superagent');

var NewsList = require('./NewsList');
var NewsForm = require('./NewsForm');

var ClubNews = React.createClass({
    render: function() {
        return (
            <div className="row">
                <div className="medium-6 columns">
                    <h5>Published news</h5><hr />
                    <NewsList club={this.props.params.slug} />
                </div>
                <div className="medium-6 columns">
                    <h5>Create news</h5><hr />
                    <NewsForm club={this.props.params.slug} />
                </div>
            </div>
        );
    }
});

module.exports = ClubNews;