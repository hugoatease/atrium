var React = require('react');
var request = require('superagent');

var ProfileSearch = React.createClass({
    getDefaultProps: function() {
        return {
            profiles: null
        }
    },

    getInitialState: function() {
        return {
            profiles: [],
            profiles_filtered: [],
            filter: null
        }
    },

    componentDidMount: function() {
        if (!this.props.profiles) {
            request.get('/api/profiles')
                .end(function(err, res) {
                    if (err) return;
                    this.setState({
                        profiles: res.body,
                        profiles_filtered: res.body
                    })
                }.bind(this));
        }
        else {
            this.setState({
                profiles: this.props.profiles,
                profiles_filtered: this.props.profiles
            });
        }
    },

    componentWillReceiveProps: function(props) {
        if (props.profiles) {
            this.setState({
                profiles: props.profiles,
                profiles_filtered: props.profiles
            });
        }
    },

    select: function(profile) {
        if (this.props.callback) {
            this.props.callback(profile);
        }
    },

    filter: function(ev) {
        var terms = ev.target.value;
        if (terms === '') {
            this.setState({terms: null});
        }
        else {
            this.setState({terms: terms});
        }

        if (this.state.terms) {
            var filtered = this.state.profiles.filter(function(profile) {
                return profile.last_name.toLowerCase().search(terms.toLowerCase()) === 0;
            });
            this.setState({profiles_filtered: filtered});
        }
    },

    render: function() {
        return (
            <div>
                <input type="text" placeholder="Filter by last name" value={this.state.filter} onChange={this.filter} />
                <div className="row small-up-2 medium-up-4" style={{overflowY: 'scroll', maxHeight: '200px'}}>
                    {this.state.profiles_filtered.map(function(profile) {
                        return (
                            <div className="column callout" onClick={this.select.bind(this, profile)}>
                                <img src={profile.photo} className="thumbnail" />
                                <p>{profile.first_name} {profile.last_name}</p>
                            </div>
                        );
                    }.bind(this))}
                </div>
            </div>
        );
    }
});

module.exports = ProfileSearch;