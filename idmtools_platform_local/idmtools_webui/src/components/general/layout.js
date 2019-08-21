import React from "react";

import { withStyles } from '@material-ui/core/styles';
import { connect } from "react-redux";
import { AppBar, Toolbar, Typography, IconButton, Button, List, ListItemIcon, ListItem, ListItemText } from "@material-ui/core";
import MenuIcon from "@material-ui/icons/Menu";
import MailIcon from '@material-ui/icons/Mail';
import InboxIcon from '@material-ui/icons/MoveToInbox';

import Divider from '@material-ui/core/Divider';
import idmlogo from '../../images/idmlogo55.png';
import Dashboard from "../views/dashboardView";

import {DASHBOARD_VIEW, EXPERIMENT_VIEW, SIMULATION_VIEW} from "../../redux/actionTypes"

import DashboardView from "../views/dashboardView"
import ExperimentView from "../views/experimentView"
import SimulationView from "../views/simulationView"
import 'react-splitter-layout/lib/index.css';


const drawerWidth = 192;


const styles = theme => ({

  root: {    
    display: 'flex',
    height:'100%'
  },
  logo: {
    display:'flex',
    padding: '10px 20px'
  },
  idmlogo: {
    //position: 'absolute',
    //clip: 'rect(0px, 45px, 100px,0px)',
    marginTop:5,
    width: 30,
    height: 30
  },

  heading:{
    color:'#a1a1a1',
    width:'100%',
    padding: '5px 8px'
  },

  content: {
    flexGrow: 1,
    backgroundColor: '#585454',
    marginLeft:`${drawerWidth}px`,
    position:'relative',
    height:'100%'
    //padding: theme.spacing(3),
  },
  appBar: {
    marginLeft: drawerWidth,
    [theme.breakpoints.up('sm')]: {
      width: `calc(100% - ${drawerWidth}px)`,
    },
  },
  toolbar: theme.mixins.toolbar,
  nav: {
    position:'fixed'
  }


});


class Layout extends React.Component {



  navigate(target) {
    return ()=> {
      
      window.location.href = "/" + target;
    }
  }

  render() {
    const { classes, simulations, selectedView } = this.props;


    
    let view = <Dashboard/>;

    if (selectedView && selectedView.selectedView == EXPERIMENT_VIEW) {
      view = <ExperimentView/>
    } else if (selectedView && selectedView.selectedView == SIMULATION_VIEW) {
      view = <SimulationView/>
    }


    return (
      <div className={classes.root}>

        <AppBar position="fixed" className={classes.appBar}>
          <Toolbar>
            <IconButton edge="start" className={classes.menuButton} color="inherit" aria-label="menu">
              <MenuIcon />
            </IconButton>
            
          </Toolbar>

        </AppBar>
        <nav className={classes.nav}>
          <div>
            <div className={classes.toolbar}>

                <div className={classes.logo}>
                  <img src={idmlogo} title="Institute for Disease Modeling" alt={"IDMlogo"} className={classes.idmlogo}></img>
                  <Typography variant="h5" className={classes.heading} >IDM Tools</Typography>
                </div>
              
            </div>
            <Divider />
            <List>
              {['Dashboard','Simulation', 'Experiment'].map((text, index) => (
                <ListItem button key={text} onClick={this.navigate(text)} >
                  <ListItemIcon>{index % 2 === 0 ? <InboxIcon /> : <MailIcon />}</ListItemIcon>
                  <ListItemText primary={text} />
                </ListItem>
              ))}
            </List>
          </div>
        </nav>

        <main className={classes.content}>
          <div className={classes.toolbar} />
          {view}
        </main>

      </div>

    )

  }
}

function mapStateToProps(state) {

  return ({
    simulations: state.simulations,
    selectedView: state.changeView
  })

}

export default connect(mapStateToProps)(withStyles(styles, { withTheme: true })(Layout));
