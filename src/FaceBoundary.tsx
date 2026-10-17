import {Component,type ReactNode} from 'react';
export default class FaceBoundary extends Component<{children:ReactNode},{failed:boolean}>{
 state={failed:false};
 static getDerivedStateFromError(){return {failed:true}}
 render(){return this.state.failed?<div className="face-study"><div className="face-viewport"><img src="/assets/face-poster.png" alt="Head preview"/></div><p className="face-note">Interactive preview unavailable.</p></div>:this.props.children}
}
