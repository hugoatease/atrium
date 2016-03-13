var React = require('react');
var request = require('superagent');
var moment = require('moment');
var browserHistory = require('react-router').browserHistory;

var NewsList = React.createClass({
    getDefaultProps: function() {
        return {
            club: null
        }
    },

    getInitialState: function() {
        return {
            news: []
        }
    },

    componentDidMount: function() {
        var r = request.get('/api/news');
        if (this.props.club) {
            r = r.query({club: this.props.club});
        }
        r.end(function (err, res) {
            if (err) return;
            this.setState({
                news: res.body
            });
        }.bind(this));
    },

    select: function(news) {
        browserHistory.push('/editor/news/' + news.id);
    },

    render: function() {
        return (
            <div>
                {this.state.news.map(function(news) {
                    var status = <span className="success label">Published</span>;
                    if (news.draft) {
                        status = <span className="alert label">Draft</span>;
                    }
                    return (
                        <div className="callout" onClick={this.select.bind(this, news)}>
                            <h5>{news.name}</h5>
                            {status}
                            <h6>On {moment(news.date).format('LL LT')} by {news.author.first_name} {news.author.last_name}</h6>
                            <p>{news.headline}</p>
                        </div>
                    );
                }.bind(this))}
            </div>
        );
    }
});

module.exports = NewsList;