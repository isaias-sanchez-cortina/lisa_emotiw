import numpy as np

import theano
from theano import config
from theano import tensor
from theano.printing import Print
from theano.compat.python2x import OrderedDict

from pylearn2.costs.cost import Cost
from pylearn2.format.target_format import OneHotFormatter
from pylearn2.models import Model
from pylearn2.space import CompositeSpace, VectorSpace
from pylearn2.termination_criteria import EpochCounter
from pylearn2.train import Train
from pylearn2.training_algorithms.sgd import SGD
from pylearn2.utils import block_gradient
from emotiw.common.datasets.faces.afew2_facetubes import AFEW2FaceTubes
from emotiw.common.datasets.faces.facetubes import FaceTubeSpace
from emotiw.wardefar.crf_theano import forward_theano as crf


class FrameMax(Model):
    """Frame based classifier, then elementwise max on top of representaions,
    and final classifier on top"""
    def __init__(self, mlp, final_layer, n_classes = None, input_source='features',
            input_space=None, pooling_mode=0, scale=False):
        """
        Parameters
        ----------
        mlp: Pylearn2 MLP class
            The frame based classifier

        final_layer: Pylearn2 MLP class
            Sequence based classifier
        pooling_mode: If 1: max_pooling
                      If 2: top_N pooling
        """

        if n_classes is None:
            if hasattr(mlp.layers[-1], 'dim'):
                self.n_classes = mlp.layers[-1].dim
            elif hasattr(mlp.layers[-1], 'n_classes'):
                self.n_classes = mlp.layers[-1].n_classes
            else:
                raise ValueError("n_classes was not provided and couldn't be infered from the mlp's last layer")
        else:
            self.n_classes = n_classes
        self.probs = np.asarray([1.2, 1., 0.8], dtype=theano.config.floatX)
        self.probs = self.probs.reshape(3, 1)
        self.scale = scale
        self.pooling_mode = pooling_mode
        self.mlp = mlp
        self.final_layer = final_layer
        self.input_source = input_source
        assert isinstance(input_space, FaceTubeSpace)
        self.input_space = input_space
        self.input_size = (input_space.shape[0]
                           * input_space.shape[1]
                           * input_space.num_channels)
        self.output_space = VectorSpace(dim=7)

    def fprop(self, inputs):

        # format inputs
        inputs = self.input_space.format_as(inputs, self.mlp.input_space)
        rval = self.mlp.fprop(inputs)
        if self.pooling_mode == 0:
            rval = tensor.max(rval, axis=0)
        elif self.pooling_mode == 1:
            rval = block_gradient(tensor.sort(rval, axis=0))[-3:][::-1]
            rval = tensor.sum(rval * self.probs, axis=0) / 3
            #rval = tensor.mean(rval, axis=0)
        else:
            raise Exception("Others are not implemented yet!")
        rval = rval.dimshuffle('x', 0)
        rval = self.final_layer.fprop(rval)

        return rval

    def dropout_fprop(self, inputs, default_input_include_prob=0.5,
                    input_include_probs=None, default_input_scale=2.,
                    input_scales=None, per_example=True):

        inputs = self.input_space.format_as(inputs, self.mlp.input_space)
        if self.scale:
            inputs = inputs / 255.
        rval = self.mlp.dropout_fprop(inputs, default_input_include_prob,
                    input_include_probs, default_input_scale,
                    input_scales, per_example)

        if self.pooling_mode == 0:
            rval = tensor.max(rval, axis=0)
        elif self.pooling_mode == 1:
            top_ids = block_gradient(tensor.sort(rval, axis=0))[-3:][::-1]
            top_vals = rval[top_ids]
            rval = T.mean(top_vals)
        elif self.pooling_mode == 2:
            #import ipdb; ipdb.set_trace()
            #collapsed_rval = tensor.sum(rval, axis=1)
            top_ids = block_gradient(tensor.argsort(rval, axis=0))[::-1]
            top_vals_sum = rval[top_ids[0], tensor.arange(rval.shape[1])] * self.probs[0]
                    #+\
                    #rval[top_ids[1], tensor.arange(rval.shape[1])] * self.probs[1]
                    #+\
                    #rval[top_ids[2], tensor.arange(rval.shape[1])] * self.probs[2]
            rval = top_vals_sum / 2
        else:
            raise Exception("Others are not implemented yet!")
        rval = rval.dimshuffle('x', 0)

        # TODO if you set input prob, the final layer doesn't recognize h0
        if input_include_probs is None and input_scales is None:
            rval = self.final_layer.dropout_fprop(rval, default_input_include_prob,
                    input_include_probs, default_input_scale,
                    input_scales, per_example)
        else:
            rval = self.final_layer.fprop(rval)

        return rval

    def get_params(self):
        return self.mlp.get_params() + self.final_layer.get_params()

    def get_lr_scalers(self):
        rval = self.mlp.get_lr_scalers()
        rval.update(self.final_layer.get_lr_scalers())
        return rval

    def get_input_source(self):
        return self.input_source

    def get_input_space(self):
        return self.input_space

    def get_monitoring_data_specs(self):
        space = CompositeSpace((self.get_input_space(),
                                VectorSpace(dim=7)))
        source = (self.get_input_source(), self.get_target_source())
        return (space, source)


    def get_monitoring_channels(self, data):

        X, Y = data
        X = self.input_space.format_as(X, self.mlp.input_space)
        X = self.mlp.fprop(X)
        X = tensor.max(X, axis=0)
        X = X.dimshuffle('x', 0)
        return self.final_layer.get_monitoring_channels((X, Y))

    def cost(self, Y, Y_hat):
        return self.final_layer.cost(Y, Y_hat)

class FrameCRF(Model):
    """Frame based classifier, then CRF on top. For detail read the
    /lisa_emotiw/emotiw/wardefar/structured_output.lyx
    """

    def __init__(self, mlp, n_classes = None, input_source='features', input_space=None, scale=False):
        """
        Parameters
        ----------
        mlp: Pylearn2 MLP class
            The frame based classifier

        """

        if n_classes is None:
            if hasattr(mlp.layers[-1], 'dim'):
                self.n_classes = mlp.layers[-1].dim
            elif hasattr(mlp.layers[-1], 'n_classes'):
                self.n_classes = mlp.layers[-1].n_classes
            else:
                raise ValueError("n_classes was not provided and couldn't be infered from the mlp's last layer")
        else:
            self.n_classes = n_classes

        self.mlp = mlp
        self.scale = scale
        self.input_source = input_source
        assert isinstance(input_space, FaceTubeSpace)
        self.input_space = input_space
        self.input_size = (input_space.shape[0]
                           * input_space.shape[1]
                           * input_space.num_channels)
        self.output_space = VectorSpace(dim=7)

        rng = self.mlp.rng
        self.W = theano.shared(rng.uniform(size=(n_classes, n_classes, n_classes)).astype(config.floatX))
        self.W.name = 'crf_w'
        self.name = 'crf'

    def fprop(self, inputs):

        # format inputs
        inputs = self.input_space.format_as(inputs, self.mlp.input_space)
        rval = self.mlp.fprop(inputs)
        rval = self.crf_fprop(rval)

        return rval

    def dropout_fprop(self, inputs, default_input_include_prob=0.5,
                    input_include_probs=None, default_input_scale=2.,
                    input_scales=None, per_example=True):

        inputs = self.input_space.format_as(inputs, self.mlp.input_space)
        if self.scale:
            inputs = inputs / 255.
        rval = self.mlp.dropout_fprop(inputs, default_input_include_prob,
                    input_include_probs, default_input_scale,
                    input_scales, per_example)
        rval = self.crf_fprop(rval)

        return rval

    def crf_fprop(self, Y_hat):

        assert hasattr(Y_hat, 'owner')
        owner = Y_hat.owner
        assert owner is not None
        op = owner.op
        if isinstance(op, Print):
            assert len(owner.inputs) == 1
            Y_hat, = owner.inputs
            owner = Y_hat.owner
            op = owner.op
        assert isinstance(op, tensor.nnet.Softmax)
        z, = owner.inputs
        assert z.ndim == 2

        z = z - z.max(axis=1).dimshuffle(0, 'x')
        log_prob = z - tensor.log(tensor.exp(z).sum(axis=1).dimshuffle(0, 'x'))
        return crf(-log_prob, self.W)

    def get_params(self):
        return self.mlp.get_params() + [self.W]

    def get_lr_scalers(self):
        return self.mlp.get_lr_scalers()

    def get_input_source(self):
        return self.input_source

    def get_input_space(self):
        return self.input_space

    def get_monitoring_data_specs(self):
        space = CompositeSpace((self.get_input_space(),
                                VectorSpace(dim=7)))
        source = (self.get_input_source(), self.get_target_source())
        return (space, source)

    def get_monitoring_channels(self, data):

        X, Y = data
        state = self.fprop(X)
        rval = OrderedDict()
        #X = self.input_space.format_as(X, self.mlp.input_space)
        #rval = self.mlp.get_monitoring_channels((X, Y))

        if Y is not None:
            # batch size is always one, so this is OK
            y_hat = tensor.argmax(state.dimshuffle('x', 0), axis=1)
            y = tensor.argmax(Y, axis=1)
            misclass = tensor.neq(y, y_hat).mean()
            misclass = tensor.cast(misclass, config.floatX)
            rval['y_misclass'] = misclass

        return rval

    def cost(self, Y, Y_hat):
        return (Y * Y_hat).sum(axis=1).mean()



