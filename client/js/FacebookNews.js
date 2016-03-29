var React = require('react');
var request = require('superagent');
var moment = require('moment');

var FacebookNews = React.createClass({
    getInitialState: function() {
        return {
            news: []
        };
    },

    componentDidMount: function() {
        request.get('/api/clubs/' + this.props.params.slug + '/facebook_posts')
            .end(function(err, res) {
                this.setState({news: res.body});
            }.bind(this));
    },

    importNews: function(id) {

    },

    render: function() {
        return (
            <div>
                <div className="row">
                    <h4>Facebook news</h4>
                    <p>Click on a news below to import it on Atrium</p>
                </div>
                <div className="row medium-up-2">
                    {this.state.news.map(function(news) {
                        return (
                            <div className="column callout" onClick={this.importNews.bind(this, news.id)}>
                                <h5>{moment(event.created_time).format('LL LT')}</h5>
                                <p>{news.message}</p>
                            </div>
                        );
                    }.bind(this))}
                </div>
            </div>
        );
    }
});

module.exports = FacebookNews;