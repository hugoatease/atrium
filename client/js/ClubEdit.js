var React = require('react');
var request = require('superagent');
var slug = require('slug');
var ReactQuill = require('react-quill');

var ClubEdit = React.createClass({
    getInitialState: function() {
        return {
            slug: this.props.params.slug,
            name: null,
            description: null
        }
    },

    fetch: function(slug) {
        if (slug) {
            request.get('/api/clubs/' + slug)
                .end(function(err, res) {
                    if (err) return;
                    this.setState(res.body);
                }.bind(this));
        }
        else {
            this.setState({
                slug: null,
                name: null,
                description: null
            })
        }
    },

    componentDidMount: function() {
        this.fetch(this.props.params.slug);
    },

    componentWillReceiveProps: function(props) {
        this.fetch(props.params.slug);
    },

    handleNameChange: function(ev) {
        var name = ev.target.value;
        var state = {name: name};

        if (!this.props.params.slug) {
            state.slug = slug(name, {lower: true});
        }

        this.setState(state);
    },

    handleDescriptionChange: function(value) {
        this.setState({
            description: value
        });
    },

    save: function() {
        request.post('/api/clubs')
            .send({
                slug: this.state.slug,
                name: this.state.name,
                description: this.state.description
            })
            .end(function(err, res) {
                if (err) return;
                alert('OK');
            });
    },

    render: function() {
        return (
            <div className="row">
                <div className="medium-6">
                    <h5>Club information</h5><hr />
                    <form onSubmit={this.save}>
                        <label>
                            <span>Slug</span>
                            <input type="text" placeholder="Club slug" value={this.state.slug} disabled="true" />
                        </label>
                        <label>
                            <span>Name</span>
                            <input type="text" placeholder="Club name" value={this.state.name} onChange={this.handleNameChange} />
                        </label>
                        <label>
                            <span>Description</span>
                            <ReactQuill placeholder="Club description" value={this.state.description} theme="snow" onChange={this.handleDescriptionChange} />
                        </label>
                        <button type="submit" className="button success">Save</button>
                    </form>
                </div>
            </div>
        )
    }
});

module.exports = ClubEdit;