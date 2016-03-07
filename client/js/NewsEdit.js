var React = require('react');
var NewsForm = require('./NewsForm');

var NewsEdit = React.createClass({
    render: function() {
        return (
            <div className="row">
                <NewsForm news_id={this.props.params.news_id} />
            </div>
        );
    }
});

module.exports = NewsEdit;